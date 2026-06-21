import { ref, computed } from 'vue'
import { inferModelName, trackFunnelEvent } from '../utils/funnelAnalytics'
import { trackAnalyticsEvent } from '../utils/analyticsTracker'

function loadCartFromStorage() {
    try {
        const raw = localStorage.getItem('denroom_cart')
        if (!raw) return []
        const parsed = JSON.parse(raw)
        if (!Array.isArray(parsed)) return []
        return parsed.map((item, idx) => {
            const config = item?.config && typeof item.config === 'object' ? { ...item.config } : {}
            const note = typeof item?.note === 'string'
                ? item.note
                : (typeof config.customer_note === 'string' ? config.customer_note : '')
            if (note) {
                config.customer_note = note
            }
            const qty = Number(item?.qty || config?.qty || 1)
            return {
                ...item,
                id: item?.id || Date.now() + idx,
                config,
                note,
                qty: qty > 0 ? qty : 1,
                price: Number(item?.price || 0)
            }
        })
    } catch (e) {
        return []
    }
}

// Simple reactive state for the cart
const cart = ref(loadCartFromStorage())
const isCartOpen = ref(false)

export const useCart = () => {
    const save = () => {
        try {
            localStorage.setItem('denroom_cart', JSON.stringify(cart.value))
        } catch (e) {
            // Ignore storage write failures so UI never crashes.
        }
    }

    const addToCart = (product, configuration) => {
        const lineId = configuration?.line_id || `line-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
        const normalizedQty = Number(configuration?.qty || product?.qty || 1)
        const qty = normalizedQty > 0 ? normalizedQty : 1
        const totalPrice = typeof configuration?.totalPrice === 'number'
            ? configuration.totalPrice
            : (typeof product?.totalPrice === 'number'
                ? product.totalPrice
                : (typeof product?.price === 'number' ? product.price : 0))
        const customerNote = typeof configuration?.customer_note === 'string' ? configuration.customer_note : ''
        const config = {
            ...(configuration || {}),
            qty,
            customer_note: customerNote
        }
        const item = {
            id: Date.now(),
            name: product.name,
            type: product.type,
            item_code: configuration?.item_code || product.item_code || product.name,
            line_id: lineId,
            parent_line_id: configuration?.parent_line_id || null,
            meta: configuration?.meta || {},
            config,
            note: customerNote,
            price: totalPrice,
            image: configuration?.image || product.images?.[0] || '',
            qty
        }
        cart.value.push(item)
        save()

        // Ignore non-product utility lines (like fabric add-ons) in funnel conversion.
        if ((item.type || '').toLowerCase() !== 'fabric') {
            trackFunnelEvent('add_to_cart', {
                model_name: inferModelName(product, configuration),
                item_code: item.item_code,
                qty: item.qty,
                amount: item.price
            })
            trackAnalyticsEvent('add_to_cart', {
                model_name: inferModelName(product, configuration),
                product_id: item.item_code,
                qty: item.qty,
                amount: item.price,
                item_group: product?.type || '',
                properties: {
                    line_id: item.line_id,
                    parent_line_id: item.parent_line_id || ''
                }
            })
        }
    }

    const updateItemNote = (id, note) => {
        const normalizedNote = (note || '').toString().trim()
        cart.value = cart.value.map((item) => {
            if (item.id !== id) return item
            const nextConfig = {
                ...(item.config && typeof item.config === 'object' ? item.config : {})
            }
            if (normalizedNote) {
                nextConfig.customer_note = normalizedNote
            } else {
                delete nextConfig.customer_note
            }
            return {
                ...item,
                note: normalizedNote,
                config: nextConfig
            }
        })
        save()
    }

    const updateItemQuantity = (id, delta) => {
        // Find the target item first to get its line_id and current qty
        const targetItem = cart.value.find((item) => item.id === id)
        if (!targetItem) return

        const oldQty = targetItem.qty || 1
        const newQty = oldQty + delta
        if (newQty < 1) return

        const ratio = newQty / oldQty

        cart.value = cart.value.map((item) => {
            // Update the target item itself
            if (item.id === id) {
                const unitPrice = (item.price || 0) / oldQty
                const newPrice = Math.round(unitPrice * newQty)
                const nextConfig = {
                    ...(item.config && typeof item.config === 'object' ? item.config : {}),
                    qty: newQty
                }
                return {
                    ...item,
                    qty: newQty,
                    price: newPrice,
                    config: nextConfig
                }
            }

            // Update linked fabric items (same parent_line_id)
            if (
                (item.type || '').toLowerCase() === 'fabric' &&
                item.config?.parent_line_id &&
                targetItem.line_id &&
                item.config.parent_line_id === targetItem.line_id
            ) {
                const oldMeters = item.config.meters || 0
                const newMeters = Math.round(oldMeters * ratio * 100) / 100
                const unitFabricPrice = (item.price || 0) / (oldMeters || 1)
                const newFabricPrice = Math.round(unitFabricPrice * newMeters)
                const nextConfig = {
                    ...(item.config && typeof item.config === 'object' ? item.config : {}),
                    meters: newMeters,
                    qty: 1
                }
                return {
                    ...item,
                    price: newFabricPrice,
                    config: nextConfig
                }
            }

            // Update linked product items (items whose parent_line_id matches this item's line_id)
            // e.g. fabric items that are children of this product — already handled above
            // Also handle child products if any
            if (
                item.config?.parent_line_id &&
                targetItem.line_id &&
                item.config.parent_line_id === targetItem.line_id &&
                (item.type || '').toLowerCase() !== 'fabric'
            ) {
                const unitPrice = (item.price || 0) / oldQty
                const newPrice = Math.round(unitPrice * newQty)
                const nextConfig = {
                    ...(item.config && typeof item.config === 'object' ? item.config : {}),
                    qty: newQty
                }
                return {
                    ...item,
                    qty: newQty,
                    price: newPrice,
                    config: nextConfig
                }
            }

            return item
        })
        save()
    }

    const removeFromCart = (id) => {
        const target = cart.value.find((item) => item.id === id)
        if (target && (target.type || '').toLowerCase() !== 'fabric') {
            trackAnalyticsEvent('remove_from_cart', {
                model_name: target?.meta?.model_name || target?.name || '',
                product_id: target.item_code || '',
                qty: target.qty || 1,
                amount: target.price || 0,
                item_group: target.type || '',
                properties: {
                    line_id: target.line_id || ''
                }
            })
        }
        cart.value = cart.value.filter(item => item.id !== id)
        save()
    }

    const clearCart = () => {
        cart.value = []
        save()
    }

    const totalItems = computed(() => cart.value.length)

    const totalPrice = computed(() =>
        cart.value.reduce((total, item) => total + item.price, 0)
    )

    return {
        cart,
        isCartOpen,
        addToCart,
        updateItemNote,
        updateItemQuantity,
        removeFromCart,
        clearCart,
        totalItems,
        totalPrice
    }
}
