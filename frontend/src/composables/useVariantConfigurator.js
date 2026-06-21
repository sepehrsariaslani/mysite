import { computed, ref, watch } from 'vue'

function buildLegacyAttributes(variant) {
  const attrs = {}
  if (!variant || typeof variant !== 'object') return attrs

  if (variant.wood) attrs['رنگ چوب'] = variant.wood
  if (variant.body_color) attrs['رنگ بدنه'] = variant.body_color
  else if (variant.body) attrs['رنگ بدنه'] = variant.body
  if (variant.height) attrs['ارتفاع'] = variant.height

  if (variant.length && variant.width) {
    attrs['ابعاد'] = `${variant.length}x${variant.width}`
  } else if (variant.length) {
    attrs['ابعاد'] = `${variant.length}`
  }

  if (variant.module) attrs['ماژول'] = variant.module
  if (variant.module_feature) attrs['ویژگی'] = variant.module_feature
  return attrs
}

function normalizeVariants(rawVariants) {
  return (rawVariants || []).map((variant) => {
    const explicitAttrs = variant?.attributes && typeof variant.attributes === 'object'
      ? { ...variant.attributes }
      : {}
    const attrs = { ...buildLegacyAttributes(variant), ...explicitAttrs }
    return {
      ...variant,
      attributes: attrs
    }
  })
}

function ensureSchema(rawSchema, normalizedVariants) {
  const schema = (rawSchema || [])
    .filter((item) => item && item.name)
    .map((item) => ({
      name: item.name,
      options: Array.from(new Set((item.options || []).filter((v) => v !== null && v !== undefined && v !== '')))
    }))

  if (schema.length) return schema

  const map = {}
  normalizedVariants.forEach((variant) => {
    Object.entries(variant.attributes || {}).forEach(([name, value]) => {
      if (value === null || value === undefined || value === '') return
      map[name] = map[name] || []
      if (!map[name].includes(value)) map[name].push(value)
    })
  })

  return Object.entries(map).map(([name, options]) => ({ name, options }))
}

function isVariantCompatibleWithSelection(variant, selection, ignoreAttr) {
  const attrs = variant.attributes || {}
  for (const [attrName, selectedValue] of Object.entries(selection || {})) {
    if (attrName === ignoreAttr) continue
    if (!selectedValue) continue
    if (attrs[attrName] !== selectedValue) return false
  }
  return true
}

export function useVariantConfigurator({ variants, attributeSchema }) {
  const selectedAttributes = ref({})

  const normalizedVariants = computed(() => normalizeVariants(variants?.value || []))
  const normalizedSchema = computed(() => ensureSchema(attributeSchema?.value || [], normalizedVariants.value))

  const availableOptionsByAttribute = computed(() => {
    const result = {}
    normalizedSchema.value.forEach((attr) => {
      const values = []
      normalizedVariants.value.forEach((variant) => {
        if (!isVariantCompatibleWithSelection(variant, selectedAttributes.value, attr.name)) return
        const value = variant.attributes?.[attr.name]
        if (value === null || value === undefined || value === '') return
        if (!values.includes(value)) values.push(value)
      })

      // keep schema ordering when available
      const ordered = (attr.options || []).filter((opt) => values.includes(opt))
      const extra = values.filter((v) => !ordered.includes(v))
      result[attr.name] = [...ordered, ...extra]
    })
    return result
  })

  const selectableAttributes = computed(() => {
    return normalizedSchema.value.map((attr) => ({
      ...attr,
      options: availableOptionsByAttribute.value[attr.name] || []
    }))
  })

  const currentVariant = computed(() => {
    if (!normalizedVariants.value.length) return null

    const schemaAttrs = normalizedSchema.value.map((a) => a.name)
    const strictMatch = normalizedVariants.value.find((variant) => {
      for (const name of schemaAttrs) {
        const selectedValue = selectedAttributes.value[name]
        if (!selectedValue) return false
        if (variant.attributes?.[name] !== selectedValue) return false
      }
      return true
    })
    if (strictMatch) return strictMatch

    return (
      normalizedVariants.value.find((variant) =>
        isVariantCompatibleWithSelection(variant, selectedAttributes.value)
      ) || normalizedVariants.value[0]
    )
  })

  const isSelectionComplete = computed(() => {
    if (!normalizedSchema.value.length) return true
    return normalizedSchema.value.every((attr) => !!selectedAttributes.value[attr.name])
  })

  function isOptionEnabled(attrName, option) {
    const options = availableOptionsByAttribute.value[attrName] || []
    return options.includes(option)
  }

  function normalizeSelection(changedAttr) {
    const next = { ...selectedAttributes.value }
    normalizedSchema.value.forEach((attr) => {
      if (changedAttr && attr.name === changedAttr) return
      const current = next[attr.name]
      const options = availableOptionsByAttribute.value[attr.name] || []
      if (current && options.includes(current)) return

      if (options.length === 1) next[attr.name] = options[0]
      else next[attr.name] = ''
    })
    selectedAttributes.value = next
  }

  function setAttribute(attrName, value) {
    if (!isOptionEnabled(attrName, value)) return
    selectedAttributes.value = { ...selectedAttributes.value, [attrName]: value }
    normalizeSelection(attrName)
  }

  function initializeSelection(preferredVariant) {
    const variantsList = normalizedVariants.value
    const schema = normalizedSchema.value
    if (!variantsList.length || !schema.length) {
      selectedAttributes.value = {}
      return
    }

    const variant = preferredVariant || variantsList[0]
    const defaults = {}
    schema.forEach((attr) => {
      const fromVariant = variant.attributes?.[attr.name]
      if (fromVariant && (attr.options || []).includes(fromVariant)) {
        defaults[attr.name] = fromVariant
      } else {
        defaults[attr.name] = attr.options?.[0] || ''
      }
    })
    selectedAttributes.value = defaults
    normalizeSelection()
  }

  watch(
    () => [normalizedVariants.value.length, normalizedSchema.value.length],
    ([variantCount, schemaCount], [prevVariantCount, prevSchemaCount]) => {
      if (!variantCount || !schemaCount) {
        selectedAttributes.value = {}
        return
      }
      if (!prevVariantCount || !prevSchemaCount) {
        initializeSelection()
      }
    },
    { immediate: true }
  )

  return {
    selectedAttributes,
    currentVariant,
    selectableAttributes,
    availableOptionsByAttribute,
    isSelectionComplete,
    isOptionEnabled,
    setAttribute,
    initializeSelection,
    normalizedVariants
  }
}
