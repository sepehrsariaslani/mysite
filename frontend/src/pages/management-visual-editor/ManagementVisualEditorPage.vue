<template>
  <div class="fig-editor" dir="rtl">
    <EditorShell :mode="mode">
      <template #top>
        <EditorTopBar
          :route="route"
          :loading="loading"
          :saving-visual="savingVisual"
          :saving-source="savingSource"
          :has-editor-target="hasEditorTarget"
          :visual-dirty="visualDirty"
          :source-dirty="sourceDirty"
          :auto-save-pending="autoSavePending"
          :auto-save-running="autoSaveRunning"
          :mode="mode"
          :active-tool="activeTool"
          :active-branch="activeBranch"
          :versioning-branches="versioningBranches"
          :component-library-summaries="componentLibrarySummaries"
          :active-library-name="activeLibraryName"
          @reload="reloadAll"
          @save-visual="saveVisualChanges"
          @save-source="saveSourceCode"
          @set-mode="setMode"
          @set-tool="setActiveTool"
          @duplicate="duplicateSelectedElement"
          @add-element="addElementToPreview"
          @create-frame-preset="createFramePresetFromToolbar"
          @boolean-op="applyBooleanOperation"
          @flatten-selection="flattenSelectedElements"
          @mask-selection="maskSelectedElements"
          @set-active-branch="setActiveBranch"
          @create-branch="createVersionBranch"
          @create-milestone="createVersionMilestone"
          @merge-branch="mergeVersionBranch"
          @set-library-name="setActiveLibraryName"
          @consume-library="consumeComponentLibraryFromServer"
          @publish-library="publishComponentLibrary"
        />
      </template>

      <template #status>
        <EditorStatusBanner :error="error" :success="success" />
      </template>

      <template #info>
        <EditorInfoBar
          v-model:selected-target-file="selectedTargetFile"
          :route="route"
          :file-info="fileInfo"
          :active-visual-override-count="activeVisualOverrideCount"
          :editable-files="editableFiles"
          @change="onTargetFileChange"
        />
      </template>

      <div v-if="!route && !selectedTargetFile" class="fig-empty-state">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <p>پارامتر <code>route</code> یا <code>target_file</code> ارسال نشده است.</p>
      </div>

      <div v-else-if="loading" class="fig-empty-state">
        <div class="fig-spinner"></div>
        <p>بارگذاری ادیتور...</p>
      </div>

      <template v-else>
        <LayersPanel
          :visual-layer-query="visualLayerQuery"
          :filtered-visual-layers="filteredVisualLayers"
          :preview-initialized="previewInitialized"
          :preview-loading="previewLoading"
          :layer-scan-in-progress="layerScanInProgress"
          :visual-selected-id="visualSelectedId"
          :visual-selected-ids="visualSelectedIds"
          :visual-layer-index="visualLayerIndex"
          :visual-children-map="visualChildrenMap"
          :asset-query="assetQuery"
          :filtered-asset-items="filteredAssetItems"
          :image-uploading="imageUploadInProgress"
          :image-library-loading="imageLibraryLoading"
          :save-note="saveNote"
          :history-versions="historyVersions"
          :restoring-version-id="restoringVersionId"
          :editor-pages="editorPages"
          :active-page-id="activeEditorPageId"
          :is-layer-expanded="isLayerExpanded"
          :set-layer-row-ref="setLayerRowRef"
          :format-date="formatDate"
          @select-page="onEditorPageSelect"
          @update:visual-layer-query="onLayerQueryInput"
          @scan-preview-layers="scanPreviewLayers"
          @toggle-layer-node="toggleLayerNode"
          @select-layer="onLayerSelect"
          @layer-drop="onLayerDrop"
          @toggle-layer-visibility="toggleLayerVisibility"
          @toggle-layer-lock="toggleLayerLock"
          @layer-context-action="onLayerContextAction"
          @rename-layer="renameVisualLayer"
          @update:asset-query="onAssetQueryInput"
          @insert-asset="insertAssetItem"
          @asset-drag-start="onAssetDragStart"
          @asset-drag-end="onAssetDragEnd"
          @upload-image-file="uploadImageAssetFromFile"
          @refresh-image-assets="refreshImageAssetLibrary"
          @update:save-note="onSaveNoteInput"
          @restore-version="restoreVersion"
        />

        <CanvasPanel
          :is-management-route="isManagementRoute"
          :is-component-file="isComponentFile"
          :component-usage-routes="componentUsageRoutes"
          :resolved-preview-scope="resolvedPreviewScope"
          :preview-initialized="previewInitialized"
          :preview-error="previewError"
          :preview-loading="previewLoading"
          :has-editor-target="hasEditorTarget"
          :preview-mode="previewMode"
          :visual-preview-src="visualPreviewSrc"
          :visual-preview-srcdoc="visualPreviewSrcdoc"
          :preview-iframe-sandbox="previewIframeSandbox"
          :viewport-preset="viewportPreset"
          :selected-visual-count="selectedVisualCount"
          :asset-drag-active="Boolean(draggingAssetItem)"
          :rulers-enabled="showRulers"
          :grid-enabled="showPixelGrid"
          :layout-grid-enabled="showLayoutGrid"
          :guides-enabled="showLayoutGuides"
          :grid-size="gridSize"
          :layout-grid-columns="layoutGridColumns"
          :nudge-step="nudgeStep"
          :nudge-step-large="nudgeStepLarge"
          :canvas-zoom="canvasZoom"
          :canvas-zoom-hud-visible="canvasZoomHudVisible"
          :canvas-zoom-hud-text="canvasZoomHudText"
          :set-frame-ref="setPreviewFrameRef"
          @update:viewport-preset="setViewportPreset"
          @align-selection="alignAndDistributeSelection"
          @drop-asset="onCanvasAssetDrop"
          @toggle-rulers="showRulers = !showRulers"
          @toggle-grid="showPixelGrid = !showPixelGrid"
          @toggle-layout-grid="showLayoutGrid = !showLayoutGrid"
          @toggle-guides="showLayoutGuides = !showLayoutGuides"
          @update:grid-size="onGridSizeInput"
          @update:layout-grid-columns="onLayoutGridColumnsInput"
          @update:nudge-step="onNudgeStepInput"
          @update:nudge-step-large="onNudgeStepLargeInput"
          @zoom-in="zoomCanvasByStep(1)"
          @zoom-out="zoomCanvasByStep(-1)"
          @zoom-fit="fitCanvasZoomToViewport"
          @zoom-reset="resetCanvasZoom"
          @request-preview-load="requestPreviewLoad"
          @frame-load="onVisualFrameLoad"
        />

        <InspectorPanel
          v-if="isDesignMode"
          :visual-selected-layer="visualSelectedLayer"
          :visual-props="visualProps"
          :selected-visual-count="selectedVisualCount"
          :selected-constraint-state="selectedConstraintState"
          :component-library-items="componentLibraryItems"
          :selected-component-id="selectedComponentId"
          :selected-component-variants="selectedComponentVariants"
          :selected-component-variant="selectedComponentVariant"
          :component-variant-draft="componentVariantDraft"
          :component-swap-target="componentSwapTarget"
          :selected-nested-component-instances="selectedNestedComponentInstances"
          :variant-property-rows="selectedVariantPropertyRows"
          :saving-visual="savingVisual"
          inspector-density="medium"
          :filtered-style-sections="filteredStyleSections"
          :inspector-style-query="inspectorStyleQuery"
          :raw-style-property-query="rawStylePropertyQuery"
          :raw-style-draft="rawStyleDraft"
          :raw-style-property-options="filteredRawStylePropertyOptions"
          :selected-layer-style-entries="selectedLayerStyleEntries"
          :raw-html-input="rawHtmlInput"
          :css-variables="filteredCssVariables"
          :css-variable-query="cssVariableQuery"
          :text-style-tokens="textStyleTokens"
          :color-style-tokens="colorStyleTokens"
          :shared-text-style-items="sharedTextStyleItems"
          :selected-shared-text-style-id="selectedSharedTextStyleId"
          :mixed-field-keys="mixedFieldKeys"
          :token-collection-items="tokenCollectionItems"
          :active-token-collection-id="activeTokenCollectionId"
          :active-token-mode="activeTokenMode"
          :token-mode-options="tokenModeOptions"
          :token-rows="activeTokenRows"
          :token-draft-name="tokenDraftName"
          :token-draft-value="tokenDraftValue"
          :token-bulk-from="tokenBulkFrom"
          :token-bulk-to="tokenBulkTo"
          :text-paragraph-preset="textParagraphPreset"
          :text-paragraph-preset-options="textParagraphPresetOptions"
          :text-open-type="textOpenType"
          :text-ligatures="textLigatures"
          :text-baseline-step="textBaselineStep"
          :text-find-query="textFindQuery"
          :text-replace-value="textReplaceValue"
          :text-replace-scope="textReplaceScope"
          :prototype-model-enabled="prototypeModel.preview_enabled"
          :prototype-frame-id-draft="prototypeFrameIdDraft"
          :prototype-frame-options="prototypeFrameOptions"
          :prototype-start-frame-id="prototypeModel.start_frame_id"
          :prototype-link-target-frame-id="prototypeLinkTargetFrameId"
          :prototype-link-transition="prototypeLinkTransition"
          :prototype-link-duration-ms="prototypeLinkDurationMs"
          :prototype-link-smart-animate="prototypeLinkSmartAnimate"
          :image-source="selectedImageSource"
          :image-target-type="selectedImageTargetType"
          :image-asset-items="filteredImageLibraryItems"
          :image-asset-query="imageAssetQuery"
          :image-library-loading="imageLibraryLoading"
          :image-uploading="imageUploadInProgress"
          :is-style-section-expanded="isStyleSectionExpanded"
          :get-field-options="getFieldOptions"
          :get-field-select-value="getFieldSelectValue"
          :should-show-custom-input="shouldShowCustomInput"
          :is-color-field="isColorFieldKey"
          :is-field-overridden="isVisualFieldOverridden"
          @duplicate-selected="duplicateSelectedElement"
          @add-element="addElementToPreview"
          @group-selection="groupSelectedElements"
          @ungroup-selection="ungroupSelectedElements"
          @set-constraint="applyConstraint"
          @set-constraint-anchor="applyConstraintAnchor"
          @create-component-master="createComponentMasterFromSelection"
          @update-component-master="updateComponentMasterFromSelection"
          @detach-component-instance="detachComponentInstanceFromSelection"
          @reset-component-overrides="resetComponentOverridesForSelection"
          @publish-component-library="publishComponentLibrary"
          @create-component-instance="createComponentInstance"
          @create-component-variant="createVariantFromSelection"
          @apply-component-variant="applyVariantToSelection"
          @update:component-variant-draft="onComponentVariantDraftInput"
          @update:component-swap-target="onComponentSwapTargetInput"
          @swap-component-instance="swapComponentInstanceFromSelection"
          @select-nested-instance="selectNestedInstanceNode"
          @set-variant-property="onVariantPropertyChange"
          @toggle-style-section="toggleStyleSection"
          @apply-visual-field="applyVisualField"
          @update:inspector-style-query="onInspectorStyleQueryInput"
          @update:raw-style-property-query="onRawStylePropertyQueryInput"
          @update:raw-style-draft="onRawStyleDraftUpdate"
          @add-raw-style="addRawStyleRule"
          @remove-raw-style="removeRawStyleRule"
          @update:raw-html-input="onRawHtmlInput"
          @apply-raw-html="applyRawHtmlToSelected"
          @update:css-variable-query="onCssVariableQueryInput"
          @update-css-variable="onCssVariableUpdate"
          @set-token-collection="setActiveTokenCollection"
          @set-token-mode="setActiveTokenMode"
          @add-token-collection="addTokenCollection"
          @update:token-draft-name="onTokenDraftNameInput"
          @update:token-draft-value="onTokenDraftValueInput"
          @add-token="addTokenToActiveCollection"
          @update-token-value="updateActiveTokenValue"
          @remove-token="removeActiveToken"
          @update:token-bulk-from="onTokenBulkFromInput"
          @update:token-bulk-to="onTokenBulkToInput"
          @apply-token-bulk-replace="applyTokenBulkReplace"
          @update:text-paragraph-preset="onTextParagraphPresetInput"
          @apply-text-paragraph-preset="applyTextParagraphPreset"
          @text-list-command="applyTextListCommand"
          @update:text-opentype="onTextOpenTypeInput"
          @update:text-ligatures="onTextLigaturesInput"
          @apply-text-opentype="applyTextOpenTypeSettings"
          @update:text-baseline-step="onTextBaselineStepInput"
          @snap-text-baseline="snapSelectedTextToBaseline"
          @update:text-find-query="onTextFindQueryInput"
          @update:text-replace-value="onTextReplaceValueInput"
          @update:text-replace-scope="onTextReplaceScopeInput"
          @apply-text-find-replace="applyTextFindReplace"
          @apply-paragraph-spacing="applyParagraphSpacing"
          @apply-inline-style-run="applyInlineStyleRun"
          @apply-inline-text-command="applyInlineTextCommand"
          @apply-shared-text-style="applySharedTextStyle"
          @detach-shared-text-style="detachSharedTextStyleFromSelection"
          @update-shared-text-style="updateSharedTextStyleFromSelection"
          @toggle-prototype-preview="togglePrototypePreview"
          @update:prototype-frame-id-draft="onPrototypeFrameIdDraftInput"
          @set-prototype-frame="setPrototypeFrameForSelection"
          @remove-prototype-frame="removePrototypeFrameForSelection"
          @set-prototype-start-frame="setPrototypeStartFrame"
          @update:prototype-link-target-frame-id="onPrototypeLinkTargetFrameIdInput"
          @update:prototype-link-transition="onPrototypeLinkTransitionInput"
          @update:prototype-link-duration-ms="onPrototypeLinkDurationMsInput"
          @toggle:prototype-link-smart-animate="togglePrototypeLinkSmartAnimate"
          @set-prototype-link="setPrototypeLinkForSelection"
          @remove-prototype-link="removePrototypeLinkForSelection"
          @update:image-asset-query="onImageAssetQueryInput"
          @refresh-image-assets="refreshImageAssetLibrary"
          @upload-image-file="uploadImageAssetFromFile"
          @apply-image-source="applyImageSourceToSelection"
          @apply-image-asset="applyImageAssetItem"
          @field-preset-change="onFieldPresetChange"
          @field-input-change="onFieldInputChange"
          @field-color-change="onFieldInputChange"
          @field-revert="onFieldRevert"
          @save-visual="saveVisualChanges"
          @reset-selected-layer="resetSelectedVisualLayer"
        />

        <DeveloperPanel
          v-else
          :snippet-tab="snippetTab"
          :css-snippet="cssSnippet"
          :html-snippet="htmlSnippet"
          :vue-snippet="vueSnippet"
          :react-snippet="reactSnippet"
          :swiftui-snippet="swiftuiSnippet"
          :compose-snippet="composeSnippet"
          :token-snippet="tokenSnippet"
          :redline-snippet="redlineSnippet"
          :full-source-preview="fullSourcePreview"
          :raw-css-preview="rawCssPreview"
          :handoff-inspect="handoffInspect"
          :handoff-redline="handoffRedline"
          :handoff-measure="handoffMeasureState"
          :source-code="sourceCode"
          :raw-css="rawCss"
          :new-element-form="newElementForm"
          :available-element-tags="availableElementTags"
          :set-source-textarea-ref="setSourceCodeTextareaRef"
          @update:snippet-tab="onSnippetTabChange"
          @update:source-code="onSourceCodeInput"
          @update:raw-css="onRawCssInput"
          @update:new-element-form="onNewElementFormUpdate"
          @insert-snippet="insertElementSnippet"
          @add-element="addElementToPreview"
        />
      </template>
    </EditorShell>
    <BottomToolDock
      :active-tool="activeTool"
      :mode="mode"
      @set-tool="setActiveTool"
      @set-mode="setMode"
    />
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, triggerRef, watch } from 'vue'
import EditorShell from './components/EditorShell.vue'
import EditorTopBar from './components/EditorTopBar.vue'
import EditorStatusBanner from './components/EditorStatusBanner.vue'
import EditorInfoBar from './components/EditorInfoBar.vue'
import LayersPanel from './components/LayersPanel.vue'
import CanvasPanel from './components/CanvasPanel.vue'
import InspectorPanel from './components/InspectorPanel.vue'
import DeveloperPanel from './components/DeveloperPanel.vue'
import BottomToolDock from './components/BottomToolDock.vue'
import { buildApiJsonHeaders, fetchJsonWithTimeout, parseJsonResponse, postEditorMethodWithFallback, resolveCsrfToken } from './composables/useEditorApi'
import { useEditorMode } from './composables/useEditorMode'
import { useDeveloperCodeView } from './composables/useDeveloperCodeView'
import LayerScannerWorker from './workers/layerScanner.worker.js?worker'
import './styles/management-visual-editor.css'

const { mode, isDesignMode, setMode } = useEditorMode()

const route = ref('')
const loading = ref(false)
const previewLoading = ref(false)
const previewInitialized = ref(false)
const previewError = ref('')
const savingVisual = ref(false)
const savingSource = ref(false)
const error = ref('')
const success = ref('')
const saveNote = ref('')
const restoringVersionId = ref('')
const visualDirty = ref(false)
const sourceDirty = ref(false)
const visualStructureDirty = ref(false)
const baselineVisualSignature = ref('')
const baselineSourceSignature = ref('')

const fileInfo = ref({ file: '', file_type: '', component: '' })
const sourceCode = ref('')
const sourceCodeTextarea = ref(null)
const rawCss = ref('')
const historyVersions = ref([])
const editableFiles = ref([])
const selectedTargetFile = ref('')
const isComponentFile = ref(false)
const componentUsageRoutes = ref([])

const visualPreviewFrame = ref(null)
const visualPreviewSrc = ref('')
const visualPreviewSrcdoc = ref('')
const visualPreviewBaseRoute = ref('')
const previewMode = ref('url')   // 'url' | 'srcdoc'
const visualLayerQuery = ref('')
const assetQuery = ref('')
const imageAssetQuery = ref('')
const imageLibraryItems = ref([])
const imageLibraryLoading = ref(false)
const imageUploadInProgress = ref(false)
const visualLayers = ref([])
const visualLayerIndex = ref({})
const visualChildrenMap = ref({})
const visualExpandedMap = ref({})
const visualLayerRowRefs = ref({})
const layerScanInProgress = ref(false)
const visualSelectedId = ref('')
const visualSelectedIds = ref([])
// shallowRef avoids deep reactivity on a potentially large map
const visualOverridesMap = shallowRef({})
const customFieldMode = ref({})
const inspectorStyleQuery = ref('')
const rawStylePropertyQuery = ref('')
const rawStyleDraft = ref({ property: 'background-color', customProperty: '', value: '' })
const rawHtmlInput = ref('')
const cssVariables = ref([])
const cssVariableQuery = ref('')
const activeTool = ref('select')
const INSERTABLE_TOOLS = new Set(['rectangle', 'text', 'frame', 'component', 'comment', 'pen'])
const FRAME_PRESET_CONFIG = {
  desktop: { width: 1440, height: 1024, label: 'Desktop Frame' },
  tablet: { width: 768, height: 1024, label: 'Tablet Frame' },
  mobile: { width: 390, height: 844, label: 'Mobile Frame' },
  card: { width: 420, height: 320, label: 'Card Frame' },
}
const DEFAULT_EDITOR_BRANCH = 'main'
const VIEWPORT_PRESET_STORAGE_KEY = 'mysite.management_editor.viewport'
const TOKEN_COLLECTION_STORAGE_KEY = 'mysite.management_editor.tokens'
const NUDGE_STEP_STORAGE_KEY = 'mysite.management_editor.nudge_step'
const NUDGE_STEP_LARGE_STORAGE_KEY = 'mysite.management_editor.nudge_step_large'
const GRID_SIZE_STORAGE_KEY = 'mysite.management_editor.grid_size'
const GRID_COLUMNS_STORAGE_KEY = 'mysite.management_editor.grid_columns'
const RULERS_STORAGE_KEY = 'mysite.management_editor.rulers'
const PIXEL_GRID_STORAGE_KEY = 'mysite.management_editor.pixel_grid'
const LAYOUT_GRID_STORAGE_KEY = 'mysite.management_editor.layout_grid'
const LAYOUT_GUIDES_STORAGE_KEY = 'mysite.management_editor.layout_guides'
const LAYOUT_GUIDE_ITEMS_STORAGE_KEY = 'mysite.management_editor.layout_guides_items'
const COMPONENT_LIBRARY_STORAGE_KEY = 'mysite.management_editor.component_library'
const SHARED_TEXT_STYLE_STORAGE_KEY = 'mysite.management_editor.shared_text_styles'
const CANVAS_ZOOM_STORAGE_KEY = 'mysite.management_editor.canvas_zoom'
const STYLE_SECTION_STORAGE_KEY = 'mysite.management_editor.style_sections'
const viewportPreset = ref('desktop')
const canvasZoom = ref(1)
const canvasZoomHudVisible = ref(false)
const canvasZoomHudText = ref('100%')
const draggingAssetItem = ref(null)
const nudgeStep = ref(1)
const nudgeStepLarge = ref(10)
const showRulers = ref(true)
const showPixelGrid = ref(false)
const showLayoutGrid = ref(false)
const showLayoutGuides = ref(true)
const gridSize = ref(8)
const layoutGridColumns = ref(12)
const layoutGuideItems = ref([])
const componentLibrary = ref({})
const componentLibrarySummaries = ref([])
const activeLibraryName = ref('global')
const activeBranch = ref('main')
const versioningBranches = ref([])
const prototypeModel = ref(defaultPrototypeModel())
const prototypeFrameIdDraft = ref('')
const prototypeLinkTargetFrameId = ref('')
const prototypeLinkTransition = ref('instant')
const prototypeLinkDurationMs = ref(280)
const prototypeLinkSmartAnimate = ref(false)
const componentVariantDraft = ref('state')
const componentSwapTarget = ref('')
const sharedTextStyles = ref({})
const tokenCollections = ref({})
const activeTokenCollectionId = ref('')
const activeTokenMode = ref('light')
const tokenDraftName = ref('')
const tokenDraftValue = ref('')
const tokenBulkFrom = ref('')
const tokenBulkTo = ref('')
const textParagraphPreset = ref('body')
const textOpenType = ref('')
const textLigatures = ref('normal')
const textBaselineStep = ref(4)
const textFindQuery = ref('')
const textReplaceValue = ref('')
const textReplaceScope = ref('selection')
const handoffMeasureState = ref({ visible: false, dx: null, dy: null, target: '' })
const availableElementTags = ['div', 'section', 'article', 'header', 'footer', 'main', 'aside', 'span', 'p', 'a', 'button', 'img', 'ul', 'li']
const newElementForm = ref({ tag: 'div', customTag: '', id: '', className: '', text: '', href: '', src: '', alt: '' })
const SELF_CLOSING_TAGS = new Set(['img', 'input', 'br', 'hr', 'meta', 'link', 'source', 'track', 'wbr'])
const COMPONENT_MASTER_ATTR = 'data-mysite-component-master'
const COMPONENT_INSTANCE_ATTR = 'data-mysite-component-instance'
const COMPONENT_VARIANT_ATTR = 'data-mysite-component-variant'
const CONSTRAINT_H_ATTR = 'data-mysite-constraint-h'
const CONSTRAINT_V_ATTR = 'data-mysite-constraint-v'
const CONSTRAINT_SIZE_ATTR = 'data-mysite-constraint-size'
const CONSTRAINT_SIZE_W_ATTR = 'data-mysite-constraint-size-w'
const CONSTRAINT_SIZE_H_ATTR = 'data-mysite-constraint-size-h'
const TEXT_STYLE_LINK_ATTR = 'data-mysite-text-style'
const LAYER_HIDDEN_ATTR = 'data-mysite-layer-hidden'
const LAYER_LOCKED_ATTR = 'data-mysite-layer-locked'
const LAYER_LABEL_ATTR = 'data-mysite-layer-label'
const LAYER_PREV_DISPLAY_ATTR = 'data-mysite-layer-prev-display'

const visualProps = ref({
  text_content: '', display: '', flexDirection: '', justifyContent: '', alignItems: '',
  flexWrap: '', flexGrow: '', flexShrink: '', gap: '', color: '', fontFamily: '', fontSize: '',
  fontWeight: '', lineHeight: '', letterSpacing: '', textAlign: '', backgroundColor: '',
  backgroundImage: '', backgroundSize: '', backgroundPosition: '', objectFit: '', objectPosition: '',
  paragraphSpacing: '',
  fontFeatureSettings: '', fontVariantLigatures: '', textIndent: '', listStyleType: '',
  listStylePosition: '', whiteSpace: '', wordSpacing: '', textTransform: '', textDecoration: '',
  borderColor: '', borderWidth: '', borderRadius: '', boxShadow: '', opacity: '',
  zIndex: '', width: '', minWidth: '', maxWidth: '', height: '', minHeight: '',
  maxHeight: '', overflowX: '', overflowY: '', margin: '', padding: '',
  transitionDuration: '', position: '', top: '', right: '', bottom: '', left: '',
  rotation: '',
})

const styleFieldOptions = {
  display: ['block', 'inline', 'inline-block', 'flex', 'inline-flex', 'grid', 'inline-grid', 'none'],
  flexDirection: ['row', 'row-reverse', 'column', 'column-reverse'],
  justifyContent: ['flex-start', 'center', 'flex-end', 'space-between', 'space-around', 'space-evenly'],
  alignItems: ['stretch', 'flex-start', 'center', 'flex-end', 'baseline'],
  flexWrap: ['nowrap', 'wrap', 'wrap-reverse'],
  flexGrow: ['0', '1'], flexShrink: ['0', '1'],
  gap: ['0', '4px', '8px', '12px', '16px', '20px', '24px', '32px'],
  color: ['inherit', '#111111', '#ffffff', '#6b7280', 'var(--text-main)', 'var(--admin-text-soft)'],
  fontFamily: [
    '\'Peyda\', sans-serif',
    '\'Vazirmatn\', sans-serif',
    '\'IRANSansX\', sans-serif',
    '\'Dana\', sans-serif',
    '\'Inter\', sans-serif',
    '\'Roboto\', sans-serif',
    '\'Georgia\', serif',
    'ui-sans-serif',
    'system-ui',
  ],
  fontSize: ['12px', '14px', '16px', '18px', '20px', '24px', '28px', '32px', '1rem', '1.25rem', '1.5rem', '2rem'],
  fontWeight: ['300', '400', '500', '600', '700', '800', '900', 'normal', 'bold'],
  lineHeight: ['normal', '1', '1.2', '1.4', '1.6', '1.8', '2'],
  letterSpacing: ['0', '0.5px', '1px', '2px'],
  textAlign: ['right', 'left', 'center', 'justify', 'start', 'end'],
  fontFeatureSettings: ['normal', '"liga" 1', '"kern" 1', '"tnum" 1', '"ss01" 1'],
  fontVariantLigatures: ['normal', 'none', 'common-ligatures', 'no-common-ligatures'],
  textIndent: ['0', '8px', '16px', '24px', '32px'],
  listStyleType: ['disc', 'decimal', 'square', 'circle', 'none'],
  listStylePosition: ['outside', 'inside'],
  whiteSpace: ['normal', 'nowrap', 'pre', 'pre-wrap'],
  wordSpacing: ['normal', '1px', '2px', '4px'],
  textTransform: ['none', 'uppercase', 'lowercase', 'capitalize'],
  textDecoration: ['none', 'underline', 'line-through', 'overline'],
  backgroundColor: ['transparent', '#ffffff', '#000000', 'var(--admin-panel-bg)', 'var(--admin-chip-bg)'],
  backgroundImage: ['none', 'url(/files/example.jpg)', 'linear-gradient(135deg,#e2e8f0,#f8fafc)'],
  backgroundSize: ['auto', 'cover', 'contain', '100% 100%'],
  backgroundPosition: ['center', 'top', 'bottom', 'left', 'right', '50% 50%'],
  borderColor: ['transparent', '#e5e7eb', '#000000', 'var(--admin-border)', 'var(--accent-gold)'],
  borderWidth: ['0', '1px', '2px', '3px', '4px'],
  borderRadius: ['0', '4px', '8px', '10px', '12px', '16px', '24px', '32px', '50%', '999px'],
  boxShadow: ['none', '0 1px 2px rgba(0,0,0,.08)', '0 8px 24px rgba(0,0,0,.12)', '0 18px 44px rgba(0,0,0,.16)', 'inset 0 1px 0 rgba(255,255,255,.45)'],
  opacity: ['1', '0.95', '0.9', '0.8', '0.7', '0.6', '0.5', '0.3', '0'],
  zIndex: ['0', '1', '2', '5', '10', '20', '50', '100'],
  width: ['auto', '100%', 'fit-content', 'min-content', 'max-content', '25%', '50%', '75%', '100vw'],
  minWidth: ['0', '120px', '160px', '200px', '240px', '320px', '50%', '100%'],
  maxWidth: ['none', '320px', '480px', '640px', '768px', '1024px', '100%'],
  height: ['auto', '100%', '50vh', '60vh', '70vh', '80vh', '100vh'],
  minHeight: ['0', '120px', '180px', '240px', '320px', '50vh', '100vh'],
  maxHeight: ['none', '240px', '320px', '480px', '640px', '100vh'],
  overflowX: ['visible', 'hidden', 'auto', 'scroll', 'clip'],
  overflowY: ['visible', 'hidden', 'auto', 'scroll', 'clip'],
  margin: ['0', '4px', '8px', '12px', '16px', '24px', '32px', '0 auto'],
  padding: ['0', '4px', '8px', '12px', '16px', '20px', '24px', '32px'],
  transitionDuration: ['0s', '0.1s', '0.15s', '0.2s', '0.3s', '0.5s', '1s'],
  position: ['static', 'relative', 'absolute', 'fixed', 'sticky'],
  top: ['auto', '0', '4px', '8px', '12px', '16px', '24px', '50%'],
  right: ['auto', '0', '4px', '8px', '12px', '16px', '24px', '50%'],
  bottom: ['auto', '0', '4px', '8px', '12px', '16px', '24px', '50%'],
  left: ['auto', '0', '4px', '8px', '12px', '16px', '24px', '50%'],
  objectFit: ['fill', 'contain', 'cover', 'none', 'scale-down'],
  objectPosition: ['center', 'top', 'bottom', 'left', 'right', '50% 50%'],
  rotation: ['0deg', '15deg', '30deg', '45deg', '90deg', '180deg'],
}

const styleSections = [
  { title: 'Position', icon: 'position', fields: [
    { key: 'position', label: 'Position' }, { key: 'top', label: 'Top' },
    { key: 'right', label: 'Right' }, { key: 'bottom', label: 'Bottom' },
    { key: 'left', label: 'Left' }, { key: 'rotation', label: 'Rotation' }, { key: 'zIndex', label: 'Z-Index' },
  ]},
  { title: 'Layout', icon: 'layout', fields: [
    { key: 'display', label: 'Display' }, { key: 'flexDirection', label: 'Direction' },
    { key: 'justifyContent', label: 'Justify' }, { key: 'alignItems', label: 'Align' },
    { key: 'gap', label: 'Gap' }, { key: 'flexWrap', label: 'Wrap' },
    { key: 'flexGrow', label: 'Grow' }, { key: 'flexShrink', label: 'Shrink' },
    { key: 'width', label: 'W' }, { key: 'height', label: 'H' },
    { key: 'minWidth', label: 'Min W' }, { key: 'maxWidth', label: 'Max W' },
    { key: 'minHeight', label: 'Min H' }, { key: 'maxHeight', label: 'Max H' },
  ]},
  { title: 'Appearance', icon: 'appearance', fields: [
    { key: 'opacity', label: 'Opacity' }, { key: 'overflowX', label: 'Overflow X' },
    { key: 'overflowY', label: 'Overflow Y' }, { key: 'margin', label: 'Margin' },
    { key: 'padding', label: 'Padding' }, { key: 'objectFit', label: 'Object Fit' },
    { key: 'objectPosition', label: 'Object Position' },
  ]},
  { title: 'Fill', icon: 'fill', fields: [
    { key: 'backgroundColor', label: 'Fill', isColor: true },
    { key: 'backgroundImage', label: 'Image' },
    { key: 'backgroundSize', label: 'Image Size' },
    { key: 'backgroundPosition', label: 'Image Position' },
  ]},
  { title: 'Stroke', icon: 'stroke', fields: [
    { key: 'borderColor', label: 'Stroke', isColor: true },
    { key: 'borderWidth', label: 'Width' },
    { key: 'borderRadius', label: 'Radius' },
  ]},
  { title: 'Effects', icon: 'effects', fields: [
    { key: 'boxShadow', label: 'Shadow' }, { key: 'transitionDuration', label: 'Transition' },
  ]},
  { title: 'Typography', icon: 'typography', fields: [
    { key: 'color', label: 'Color', isColor: true }, { key: 'fontFamily', label: 'Family' }, { key: 'fontSize', label: 'Size' },
    { key: 'fontWeight', label: 'Weight' }, { key: 'lineHeight', label: 'Line H' },
    { key: 'letterSpacing', label: 'Spacing' }, { key: 'textAlign', label: 'Align' },
    { key: 'fontFeatureSettings', label: 'OpenType' }, { key: 'fontVariantLigatures', label: 'Ligatures' },
    { key: 'textIndent', label: 'Indent' }, { key: 'listStyleType', label: 'List Type' },
    { key: 'listStylePosition', label: 'List Pos' }, { key: 'whiteSpace', label: 'Whitespace' },
    { key: 'wordSpacing', label: 'Word Spc' }, { key: 'textTransform', label: 'Transform' },
    { key: 'textDecoration', label: 'Decoration' },
  ]},
]

const DEFAULT_STYLE_SECTION_OPEN = styleSections.reduce(
  (acc, s) => ({ ...acc, [s.title]: true }),
  {
    __text__: true,
    __image_basic__: true,
    __typography_basic__: true,
    __position_basic__: true,
    __autolayout__: true,
    __fill_basic__: true,
    __stroke_basic__: true,
    __effects_basic__: true,
    __shared_text_style__: true,
    __text_runs__: true,
    __textengine__: true,
    __constraints__: true,
    __prototype__: true,
    __component__: true,
    __rawcss__: true,
    __rawhtml__: true,
    __all_properties__: true,
    __variables__: true,
    __styles__: true,
    __tokens__: true,
  }
)

function readStyleSectionOpenFromStorage() {
  try {
    if (typeof window === 'undefined') return { ...DEFAULT_STYLE_SECTION_OPEN }
    const raw = window.localStorage.getItem(STYLE_SECTION_STORAGE_KEY)
    const parsed = raw ? JSON.parse(raw) : {}
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return { ...DEFAULT_STYLE_SECTION_OPEN }
    const output = { ...DEFAULT_STYLE_SECTION_OPEN }
    for (const [key, value] of Object.entries(parsed)) output[String(key || '')] = value !== false
    return output
  } catch {
    return { ...DEFAULT_STYLE_SECTION_OPEN }
  }
}

const styleSectionOpen = ref(readStyleSectionOpenFromStorage())

const VISUAL_NODE_ATTR = 'data-mysite-node'
const PAYLOAD_TIMEOUT_MS = 45000
const PREVIEW_TIMEOUT_MS = 12000
const AUTO_SAVE_DEBOUNCE_MS = 1400
const AUTO_SAVE_RETRY_DELAY_MS = 2600
const AUTO_SAVE_MAX_RETRIES = 3
const LAYER_SCAN_CHUNK_MS = 8
const MAX_VISUAL_LAYER_SCAN_MS = 3200
const MAX_VISUAL_CHILDREN_PER_NODE = 220
const MAX_VISUAL_LAYER_NODES = 2200
const MAX_VISUAL_LAYER_DEPTH = 20
const LAYER_SCAN_WORKER_TIMEOUT_MS = 5200
const LAYER_SCAN_WORKER_MIN_HTML_LEN = 18000
const CRASH_RECOVERY_STORAGE_KEY = 'mysite.management_editor.crash_recovery'
const CRASH_RECOVERY_MAX_SERIALIZED = 2_000_000
const CLICK_THROTTLE_MS = 160
const COMPUTED_STYLE_IDLE_TIMEOUT_MS = 260
const COMPUTED_STYLE_FALLBACK_DELAY_MS = 140
const MAX_VISUAL_HISTORY_ITEMS = 80

let visualFrameDocument = null
let visualSelectedElement = null
let visualFrameClickHandler = null
let visualFrameDblClickHandler = null
let visualFramePointerDownHandler = null
let visualFramePointerMoveHandler = null
let visualFramePointerUpHandler = null
let visualFrameWheelHandler = null
let visualFrameKeyDownHandler = null
let visualFrameKeyUpHandler = null
let visualFrameAnchorBlockHandler = null
let visualFrameSubmitBlockHandler = null
let visualFrameScrollHandler = null
let visualResizeOverlay = null
let visualResizeMoveHandler = null
let visualResizeUpHandler = null
let resizeState = null
let rotateState = null
let visualGuideOverlay = null
let visualGuideV = null
let visualGuideH = null
let visualGuideLabelV = null
let visualGuideLabelH = null
let visualFlowInsertionLine = null
let visualMarqueeOverlay = null
let visualMarqueeMoveHandler = null
let visualMarqueeUpHandler = null
let marqueeState = null
let visualGridOverlay = null
let visualLayoutColumnsOverlay = null
let visualRulersOverlay = null
let visualLayoutGuideLayer = null
let visualMeasureOverlay = null
let visualMeasureLineX = null
let visualMeasureLineY = null
let visualMeasureLabelX = null
let visualMeasureLabelY = null
let visualRedlineOverlay = null
let visualRedlineLineX = null
let visualRedlineLineY = null
let visualRedlineLabelX = null
let visualRedlineLabelY = null
let visualGuideDragMoveHandler = null
let visualGuideDragUpHandler = null
let visualFrameMeasureMoveHandler = null
let suppressFrameClickOnce = false
let inlineTextEditState = null
let visualTextToolbar = null
let previewTimeoutHandle = null
let payloadAbortController = null
let previewFrameLoadToken = 0
let visualLayerScanToken = 0
let dirtyDebounceTimer = null  // ⚡ debounce dirty state
let pendingSelectionFrameHandle = null
let autoSaveTimer = null
let autoSaveRetryCount = 0
let frameDragState = null
let framePanState = null
let canvasSpacePressed = false
let canvasZoomHudTimer = null
let visualClipboardHtml = ''
let visualUndoStack = []
let visualRedoStack = []
let visualLastHistoryPushAt = 0
let visualRestoringHistory = false
let appliedTokenNames = new Set()
let layerScanWorker = null
let layerScanWorkerRequestId = 0
let crashRecoveryPersistTimer = null
let crashRecoveryPromptedSessionKey = ''
let visualStructureObserver = null
let visualStructureObserverIgnoreUntil = 0

const autoSaveEnabled = ref(true)
const autoSavePending = ref(false)
const autoSaveRunning = ref(false)

const isManagementRoute = computed(() => String(route.value || '').trim().startsWith('/mysite/management'))
const hasEditorTarget = computed(() => Boolean(String(route.value || '').trim() || String(selectedTargetFile.value || '').trim() || String(fileInfo.value?.file || '').trim()))
const resolvedPreviewScope = computed(() => (isComponentFile.value ? 'component' : 'page'))
const previewIframeSandbox = computed(() => {
  if (resolvedPreviewScope.value === 'component') return 'allow-same-origin allow-forms allow-popups'
  return 'allow-same-origin allow-scripts allow-forms allow-popups'
})
const activeVisualOverrideCount = computed(
  () =>
    Object.values(visualOverridesMap.value || {}).filter((row) => {
      const styles = row?.styles && typeof row.styles === 'object' ? row.styles : {}
      return Object.keys(styles).length > 0 || Boolean(row?.apply_text) || Boolean(row?.apply_html)
    }).length
)
const activeEditorPageId = computed(() => {
  const routeKey = String(route.value || '').trim()
  if (routeKey) return routeKey
  const fileKey = String(selectedTargetFile.value || '').trim()
  return fileKey ? `file:${fileKey}` : ''
})
const editorPages = computed(() => {
  const rows = []
  const seen = new Set()
  const pushRoute = (rawRoute, description = '') => {
    const normalized = normalizeEditorRoute(rawRoute)
    if (!normalized || seen.has(normalized)) return
    seen.add(normalized)
    rows.push({
      id: normalized,
      label: normalizeEditorPageLabel(normalized),
      description: String(description || '').trim(),
    })
  }
  pushRoute(route.value, 'Active')
  for (const usageRoute of Array.isArray(componentUsageRoutes.value) ? componentUsageRoutes.value : []) {
    pushRoute(usageRoute, 'Component usage')
  }
  const fileKey = String(selectedTargetFile.value || '').trim()
  if (fileKey) {
    const fileId = `file:${fileKey}`
    if (!seen.has(fileId)) {
      rows.push({
        id: fileId,
        label: `File: ${fileKey.split('/').slice(-2).join('/') || fileKey}`,
        description: fileKey,
      })
    }
  }
  return rows
})

function normalizeEditorRoute(value) {
  let routeValue = String(value || '').trim()
  if (!routeValue) return ''
  if (/^https?:\/\//i.test(routeValue)) {
    try {
      const parsed = new URL(routeValue, window.location.origin)
      routeValue = `${parsed.pathname || ''}${parsed.search || ''}`
    } catch { /* noop */ }
  }
  const [pathOnlyRaw] = routeValue.split('?')
  const pathOnly = String(pathOnlyRaw || '').trim()
  if (!pathOnly.startsWith('/mysite')) return ''
  if (pathOnly.startsWith('/mysite/management')) return ''
  if (pathOnly === '/default-route-fallback' || pathOnly.endsWith('/default-route-fallback')) return ''
  return routeValue
}

function normalizeEditorPageLabel(routeValue) {
  const normalized = normalizeEditorRoute(routeValue)
  if (!normalized) return 'Untitled'
  const [pathOnly] = normalized.split('?')
  const cleanPath = String(pathOnly || '').replace(/\/+$/, '')
  const leaf = cleanPath.split('/').filter(Boolean).pop()
  if (leaf) return leaf
  return cleanPath || normalized
}

function isLayerExpanded(nodeId) {
  const key = String(nodeId || '').trim()
  if (!key) return true
  return visualExpandedMap.value?.[key] !== false
}

function setLayerRowRef(nodeId, el) {
  const key = String(nodeId || '').trim()
  if (!key) return
  if (el) visualLayerRowRefs.value[key] = el
  else delete visualLayerRowRefs.value[key]
  // no triggerRef needed – row refs only used imperatively, not in computed
}

function toggleLayerNode(nodeId) {
  const key = String(nodeId || '').trim()
  if (!key) return
  if (Number(visualLayerIndex.value?.[key]?.child_count || 0) <= 0) return
  // Direct mutation + triggerRef (O(1) instead of spreading whole map)
  visualExpandedMap.value[key] = !isLayerExpanded(key)
  triggerRef(visualExpandedMap)
}

function normalizeLayerSearchText(layer) {
  return `${layer?.label || ''} ${layer?.tag || ''} ${layer?.selector || ''}`.toLowerCase()
}

const filteredVisualLayers = computed(() => {
  const term = visualLayerQuery.value.trim().toLowerCase()
  const rows = Array.isArray(visualLayers.value) ? visualLayers.value : []
  if (!rows.length) return []
  const index = visualLayerIndex.value || {}
  const childrenMap = visualChildrenMap.value || {}
  const roots = Array.isArray(childrenMap.__root__) ? childrenMap.__root__ : rows.filter((row) => !row.parent_id).map((row) => row.id)

  const result = []
  if (!term) {
    const walk = (nodeId) => {
      const layer = index?.[nodeId]
      if (!layer) return
      result.push(layer)
      if (!isLayerExpanded(nodeId)) return
      const children = Array.isArray(childrenMap[nodeId]) ? childrenMap[nodeId] : []
      for (const childId of children) walk(childId)
    }
    for (const rootId of roots) walk(rootId)
    return result
  }

  const includeSet = new Set()
  const includeDescendants = (nodeId) => {
    const children = Array.isArray(childrenMap[nodeId]) ? childrenMap[nodeId] : []
    for (const childId of children) {
      if (includeSet.has(childId)) continue
      includeSet.add(childId)
      includeDescendants(childId)
    }
  }
  const includeAncestors = (nodeId) => {
    let current = index?.[nodeId]
    while (current) {
      includeSet.add(current.id)
      const parentId = String(current.parent_id || '').trim()
      current = parentId ? index?.[parentId] : null
    }
  }
  for (const row of rows) {
    if (!normalizeLayerSearchText(row).includes(term)) continue
    includeAncestors(row.id)
    includeDescendants(row.id)
  }
  const walkAll = (nodeId) => {
    const layer = index?.[nodeId]
    if (!layer) return
    if (includeSet.has(nodeId)) result.push(layer)
    const children = Array.isArray(childrenMap[nodeId]) ? childrenMap[nodeId] : []
    for (const childId of children) walkAll(childId)
  }
  for (const rootId of roots) walkAll(rootId)
  return result
})

const visualSelectedLayer = computed(() => {
  if (!visualSelectedId.value) return null
  return visualLayerIndex.value?.[visualSelectedId.value] || null
})

const selectedVisualCount = computed(() => {
  const ids = Array.isArray(visualSelectedIds.value) ? visualSelectedIds.value : []
  return ids.length
})

const selectedComponentId = computed(() => {
  if (!visualSelectedElement) return ''
  return String(
    visualSelectedElement.getAttribute(COMPONENT_INSTANCE_ATTR) ||
    visualSelectedElement.getAttribute(COMPONENT_MASTER_ATTR) ||
    ''
  ).trim()
})

const selectedConstraintState = computed(() => {
  if (!visualSelectedElement) return { horizontal: 'left', vertical: 'top', size: 'fixed', sizeWidth: 'fixed', sizeHeight: 'fixed' }
  const size = String(visualSelectedElement.getAttribute(CONSTRAINT_SIZE_ATTR) || 'fixed')
  const sizeWidth = String(visualSelectedElement.getAttribute(CONSTRAINT_SIZE_W_ATTR) || size || 'fixed')
  const sizeHeight = String(visualSelectedElement.getAttribute(CONSTRAINT_SIZE_H_ATTR) || size || 'fixed')
  return {
    horizontal: String(visualSelectedElement.getAttribute(CONSTRAINT_H_ATTR) || 'left'),
    vertical: String(visualSelectedElement.getAttribute(CONSTRAINT_V_ATTR) || 'top'),
    size,
    sizeWidth,
    sizeHeight,
  }
})

const componentLibraryItems = computed(() =>
  Object.values(componentLibrary.value || {}).sort((a, b) => String(a?.name || '').localeCompare(String(b?.name || '')))
)

const prototypeFrameOptions = computed(() => {
  const rows = Object.values(prototypeModel.value?.frames || {})
    .filter((row) => row && typeof row === 'object')
    .map((row) => {
      const id = String(row.id || '').trim()
      const selector = String(row.selector || '').trim()
      const label = String(row.label || id || selector).trim() || id || selector
      return { id, selector, label: id ? `${id} — ${label}` : label }
    })
    .filter((row) => row.id && row.selector)
  rows.sort((a, b) => a.id.localeCompare(b.id))
  return rows
})

const textParagraphPresetOptions = [
  { key: 'body', label: 'Body', styles: { fontSize: '16px', lineHeight: '1.7', fontWeight: '400', letterSpacing: '0' } },
  { key: 'caption', label: 'Caption', styles: { fontSize: '12px', lineHeight: '1.4', fontWeight: '400', letterSpacing: '0.2px' } },
  { key: 'heading-sm', label: 'Heading S', styles: { fontSize: '20px', lineHeight: '1.45', fontWeight: '600', letterSpacing: '0' } },
  { key: 'heading-md', label: 'Heading M', styles: { fontSize: '28px', lineHeight: '1.35', fontWeight: '700', letterSpacing: '-0.2px' } },
  { key: 'heading-lg', label: 'Heading L', styles: { fontSize: '40px', lineHeight: '1.25', fontWeight: '700', letterSpacing: '-0.4px' } },
]

function normalizeTokenName(value) {
  let text = String(value || '').trim()
  if (!text) return ''
  if (!text.startsWith('--')) text = `--${text.replace(/^[-]+/, '')}`
  text = text.replace(/[^a-zA-Z0-9_-]/g, '-').replace(/-{2,}/g, '-')
  text = text.replace(/^--+/, '--')
  if (!/^--[a-zA-Z0-9_-]+$/.test(text)) return ''
  return text.slice(0, 80)
}

function defaultTokenCollections() {
  return {
    core: {
      id: 'core',
      name: 'Core',
      modes: {
        light: {
          '--color-surface': '#ffffff',
          '--color-text': '#0f172a',
          '--color-primary': '#0d99ff',
        },
        dark: {
          '--color-surface': '#111827',
          '--color-text': '#f8fafc',
          '--color-primary': '#38bdf8',
        },
        brand: {
          '--color-surface': '#fff8ef',
          '--color-text': '#2f1d12',
          '--color-primary': '#d18b1f',
        },
      },
    },
  }
}

function normalizeTokenCollections(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) return defaultTokenCollections()
  const output = {}
  for (const [rawId, rawCollection] of Object.entries(input)) {
    const id = String(rawId || '').trim()
    if (!id || !rawCollection || typeof rawCollection !== 'object') continue
    const name = String(rawCollection.name || id).trim() || id
    const rawModes = rawCollection.modes && typeof rawCollection.modes === 'object' ? rawCollection.modes : {}
    const modes = {}
    for (const [rawMode, rawTokens] of Object.entries(rawModes)) {
      const mode = String(rawMode || '').trim().toLowerCase()
      if (!mode || !rawTokens || typeof rawTokens !== 'object') continue
      const tokens = {}
      for (const [rawTokenName, rawValue] of Object.entries(rawTokens)) {
        const tokenName = normalizeTokenName(rawTokenName)
        const tokenValue = String(rawValue || '').trim()
        if (!tokenName || !tokenValue) continue
        tokens[tokenName] = tokenValue.slice(0, 600)
      }
      modes[mode] = tokens
    }
    if (!Object.keys(modes).length) modes.light = {}
    output[id] = { id, name, modes }
  }
  if (!Object.keys(output).length) return defaultTokenCollections()
  return output
}

const tokenCollectionItems = computed(() =>
  Object.values(tokenCollections.value || {}).map((row) => ({ id: String(row.id || ''), name: String(row.name || row.id || '').trim() || String(row.id || '') }))
)

const activeTokenCollection = computed(() => {
  const id = String(activeTokenCollectionId.value || '').trim()
  return tokenCollections.value?.[id] || null
})

const tokenModeOptions = computed(() => {
  const modes = Object.keys(activeTokenCollection.value?.modes || {})
  if (!modes.length) return ['light']
  const baseOrder = ['light', 'dark', 'brand']
  const ordered = []
  for (const item of baseOrder) if (modes.includes(item)) ordered.push(item)
  for (const item of modes) if (!ordered.includes(item)) ordered.push(item)
  return ordered
})

function resolveTokenAliasValue(tokenMap, tokenName, depth = 0, stack = new Set()) {
  const name = normalizeTokenName(tokenName)
  if (!name) return { value: '', cycle: false, alias: '' }
  if (depth > 20) return { value: '', cycle: true, alias: name }
  if (stack.has(name)) return { value: '', cycle: true, alias: name }
  const rawValue = String(tokenMap?.[name] || '').trim()
  if (!rawValue) return { value: '', cycle: false, alias: '' }
  const aliasByAt = rawValue.startsWith('@') ? normalizeTokenName(rawValue.slice(1)) : ''
  const aliasByVar = (() => {
    const match = rawValue.match(/^var\(\s*(--[A-Za-z0-9_-]+)\s*\)$/)
    return match ? normalizeTokenName(match[1]) : ''
  })()
  const aliasTarget = aliasByAt || aliasByVar
  if (!aliasTarget) return { value: rawValue, cycle: false, alias: '' }
  const nextStack = new Set(stack)
  nextStack.add(name)
  const nested = resolveTokenAliasValue(tokenMap, aliasTarget, depth + 1, nextStack)
  if (nested.cycle) return { value: '', cycle: true, alias: aliasTarget }
  return { value: nested.value || '', cycle: false, alias: aliasTarget }
}

function countTokenUsage(tokenName) {
  const token = normalizeTokenName(tokenName)
  if (!token) return 0
  const varPattern = new RegExp(`var\\(\\s*${escapeRegex(token)}\\s*\\)`, 'gi')
  const aliasName = token.replace(/^--/, '')
  const aliasPattern = new RegExp(`@(?:--)?${escapeRegex(aliasName)}\\b`, 'gi')
  let count = 0
  const countIn = (text) => {
    const source = String(text || '')
    if (!source) return
    const matches = source.match(varPattern)
    if (matches?.length) count += matches.length
    const aliasMatches = source.match(aliasPattern)
    if (aliasMatches?.length) count += aliasMatches.length
  }
  countIn(sourceCode.value)
  countIn(rawCss.value)
  for (const row of Object.values(visualOverridesMap.value || {})) {
    if (!row || typeof row !== 'object') continue
    for (const value of Object.values(row.styles || {})) countIn(value)
    if (row.apply_html) countIn(row.html_content)
  }
  for (const collection of Object.values(tokenCollections.value || {})) {
    for (const modeTokens of Object.values(collection?.modes || {})) {
      for (const value of Object.values(modeTokens || {})) countIn(value)
    }
  }
  return count
}

const activeTokenRows = computed(() => {
  const tokens = activeTokenCollection.value?.modes?.[activeTokenMode.value] || {}
  const names = Object.keys(tokens || {}).sort((a, b) => a.localeCompare(b))
  return names.map((name) => {
    const rawValue = String(tokens[name] || '')
    const resolved = resolveTokenAliasValue(tokens, name)
    return {
      name,
      rawValue,
      resolvedValue: resolved.value,
      aliasTarget: resolved.alias,
      hasCycle: resolved.cycle,
      usageCount: countTokenUsage(name),
    }
  })
})

function cloneTokenCollections(value) {
  try {
    return normalizeTokenCollections(JSON.parse(JSON.stringify(value || {})))
  } catch {
    return normalizeTokenCollections(value || {})
  }
}

function normalizeTokenValueInput(value) {
  const raw = String(value || '').trim()
  if (!raw) return ''
  if (raw.startsWith('@')) {
    const alias = normalizeTokenName(raw.slice(1))
    if (!alias) return ''
    return `@${alias.replace(/^--/, '')}`
  }
  return raw.slice(0, 600)
}

function resolveActiveTokenSelection(collectionsInput, preferredCollectionId = '', preferredMode = 'light') {
  const collections = normalizeTokenCollections(collectionsInput)
  const firstCollectionId = Object.keys(collections)[0] || 'core'
  const collectionId = collections[preferredCollectionId] ? preferredCollectionId : firstCollectionId
  const modeMap = collections?.[collectionId]?.modes || {}
  const modes = Object.keys(modeMap)
  let mode = String(preferredMode || 'light').trim().toLowerCase() || 'light'
  if (!modes.includes(mode)) mode = modes.includes('light') ? 'light' : (modes[0] || 'light')
  return { collectionId, mode, collections }
}

function readTokenStateFromStorage() {
  try {
    const raw = window.localStorage.getItem(TOKEN_COLLECTION_STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object') return null
    const collections = normalizeTokenCollections(parsed.collections || parsed.token_collections || {})
    const preferredCollection = String(parsed.active_collection || parsed.token_active_collection || '').trim()
    const preferredMode = String(parsed.active_mode || parsed.token_active_mode || 'light').trim().toLowerCase() || 'light'
    const selection = resolveActiveTokenSelection(collections, preferredCollection, preferredMode)
    return {
      collections: selection.collections,
      activeCollectionId: selection.collectionId,
      activeMode: selection.mode,
    }
  } catch {
    return null
  }
}

function persistTokenStateToStorage() {
  try {
    const payload = {
      collections: cloneTokenCollections(tokenCollections.value),
      active_collection: String(activeTokenCollectionId.value || ''),
      active_mode: String(activeTokenMode.value || 'light'),
    }
    window.localStorage.setItem(TOKEN_COLLECTION_STORAGE_KEY, JSON.stringify(payload))
  } catch {
    // noop
  }
}

function convertTokenValueToRuntime(value) {
  const raw = String(value || '').trim()
  if (!raw) return ''
  if (raw.startsWith('@')) {
    const alias = normalizeTokenName(raw.slice(1))
    if (!alias) return ''
    return `var(${alias})`
  }
  return raw
}

function applyActiveTokenModeToDocument(doc) {
  if (!doc?.documentElement) return
  const tokens = activeTokenCollection.value?.modes?.[activeTokenMode.value] || {}
  const root = doc.documentElement
  const nextNames = new Set()
  for (const [rawName, rawValue] of Object.entries(tokens || {})) {
    const tokenName = normalizeTokenName(rawName)
    const runtimeValue = convertTokenValueToRuntime(rawValue)
    if (!tokenName || !runtimeValue) continue
    root.style.setProperty(tokenName, runtimeValue)
    nextNames.add(tokenName)
  }
  for (const oldName of Array.from(appliedTokenNames || [])) {
    if (nextNames.has(oldName)) continue
    root.style.removeProperty(oldName)
  }
  appliedTokenNames = nextNames
}

function getSelectedNodeIds() {
  if (Array.isArray(visualSelectedIds.value) && visualSelectedIds.value.length) {
    return visualSelectedIds.value.map((row) => String(row || '').trim()).filter(Boolean)
  }
  const id = String(visualSelectedId.value || '').trim()
  return id ? [id] : []
}

function setActiveTokenCollection(collectionId) {
  const desired = String(collectionId || '').trim()
  const selection = resolveActiveTokenSelection(tokenCollections.value, desired, activeTokenMode.value)
  tokenCollections.value = selection.collections
  activeTokenCollectionId.value = selection.collectionId
  activeTokenMode.value = selection.mode
  applyActiveTokenModeToDocument(visualFrameDocument)
  collectPreviewCssVariables(visualFrameDocument)
}

function setActiveTokenMode(modeValue) {
  const nextMode = String(modeValue || '').trim().toLowerCase() || 'light'
  const selection = resolveActiveTokenSelection(tokenCollections.value, activeTokenCollectionId.value, nextMode)
  tokenCollections.value = selection.collections
  activeTokenCollectionId.value = selection.collectionId
  activeTokenMode.value = selection.mode
  applyActiveTokenModeToDocument(visualFrameDocument)
  collectPreviewCssVariables(visualFrameDocument)
}

function onTokenDraftNameInput(value) {
  tokenDraftName.value = String(value || '')
}

function onTokenDraftValueInput(value) {
  tokenDraftValue.value = String(value || '')
}

function onTokenBulkFromInput(value) {
  tokenBulkFrom.value = String(value || '')
}

function onTokenBulkToInput(value) {
  tokenBulkTo.value = String(value || '')
}

function addTokenCollection() {
  const next = cloneTokenCollections(tokenCollections.value)
  let idx = 1
  let id = `collection-${idx}`
  while (next[id]) {
    idx += 1
    id = `collection-${idx}`
  }
  next[id] = {
    id,
    name: `Collection ${idx}`,
    modes: {
      light: {},
      dark: {},
      brand: {},
    },
  }
  const selection = resolveActiveTokenSelection(next, id, 'light')
  tokenCollections.value = selection.collections
  activeTokenCollectionId.value = selection.collectionId
  activeTokenMode.value = selection.mode
  tokenDraftName.value = ''
  tokenDraftValue.value = ''
  success.value = 'Collection جدید ساخته شد.'
  error.value = ''
  applyActiveTokenModeToDocument(visualFrameDocument)
  collectPreviewCssVariables(visualFrameDocument)
}

function addTokenToActiveCollection() {
  const tokenName = normalizeTokenName(tokenDraftName.value)
  const tokenValue = normalizeTokenValueInput(tokenDraftValue.value)
  if (!tokenName || !tokenValue) return
  const next = cloneTokenCollections(tokenCollections.value)
  const selection = resolveActiveTokenSelection(next, activeTokenCollectionId.value, activeTokenMode.value)
  if (!selection.collections[selection.collectionId].modes[selection.mode]) {
    selection.collections[selection.collectionId].modes[selection.mode] = {}
  }
  selection.collections[selection.collectionId].modes[selection.mode][tokenName] = tokenValue
  tokenCollections.value = selection.collections
  activeTokenCollectionId.value = selection.collectionId
  activeTokenMode.value = selection.mode
  tokenDraftName.value = ''
  tokenDraftValue.value = ''
  success.value = 'Token اضافه شد.'
  error.value = ''
  applyActiveTokenModeToDocument(visualFrameDocument)
  collectPreviewCssVariables(visualFrameDocument)
}

function updateActiveTokenValue(tokenName, tokenValue) {
  const name = normalizeTokenName(tokenName)
  if (!name) return
  const value = normalizeTokenValueInput(tokenValue)
  const next = cloneTokenCollections(tokenCollections.value)
  const selection = resolveActiveTokenSelection(next, activeTokenCollectionId.value, activeTokenMode.value)
  const modeTokens = selection.collections[selection.collectionId]?.modes?.[selection.mode]
  if (!modeTokens || typeof modeTokens !== 'object') return
  if (value) modeTokens[name] = value
  else delete modeTokens[name]
  tokenCollections.value = selection.collections
  activeTokenCollectionId.value = selection.collectionId
  activeTokenMode.value = selection.mode
  applyActiveTokenModeToDocument(visualFrameDocument)
  collectPreviewCssVariables(visualFrameDocument)
}

function removeActiveToken(tokenName) {
  const name = normalizeTokenName(tokenName)
  if (!name) return
  const next = cloneTokenCollections(tokenCollections.value)
  const selection = resolveActiveTokenSelection(next, activeTokenCollectionId.value, activeTokenMode.value)
  const modeTokens = selection.collections[selection.collectionId]?.modes?.[selection.mode]
  if (!modeTokens || typeof modeTokens !== 'object') return
  delete modeTokens[name]
  tokenCollections.value = selection.collections
  activeTokenCollectionId.value = selection.collectionId
  activeTokenMode.value = selection.mode
  success.value = 'Token حذف شد.'
  error.value = ''
  applyActiveTokenModeToDocument(visualFrameDocument)
  collectPreviewCssVariables(visualFrameDocument)
}

function replaceTokenReferencesInText(sourceText, fromToken, toToken) {
  const source = String(sourceText || '')
  if (!source) return { text: source, count: 0 }
  const fromName = normalizeTokenName(fromToken)
  const toName = normalizeTokenName(toToken)
  if (!fromName || !toName || fromName === toName) return { text: source, count: 0 }
  const aliasFrom = fromName.replace(/^--/, '')
  const aliasTo = toName.replace(/^--/, '')
  const patterns = [
    {
      re: new RegExp(`var\\(\\s*${escapeRegex(fromName)}\\s*\\)`, 'gi'),
      to: `var(${toName})`,
    },
    {
      re: new RegExp(`@(?:--)?${escapeRegex(aliasFrom)}\\b`, 'gi'),
      to: `@${aliasTo}`,
    },
  ]
  let next = source
  let count = 0
  for (const pattern of patterns) {
    const matches = next.match(pattern.re)
    if (matches?.length) count += matches.length
    next = next.replace(pattern.re, pattern.to)
  }
  return { text: next, count }
}

function applyTokenBulkReplace() {
  const fromToken = normalizeTokenName(tokenBulkFrom.value)
  const toToken = normalizeTokenName(tokenBulkTo.value)
  if (!fromToken || !toToken || fromToken === toToken) return
  let replaceCount = 0

  const nextCollections = cloneTokenCollections(tokenCollections.value)
  for (const collection of Object.values(nextCollections || {})) {
    for (const modeTokens of Object.values(collection?.modes || {})) {
      if (!modeTokens || typeof modeTokens !== 'object') continue
      if (Object.prototype.hasOwnProperty.call(modeTokens, fromToken)) {
        if (!Object.prototype.hasOwnProperty.call(modeTokens, toToken)) {
          modeTokens[toToken] = modeTokens[fromToken]
        }
        delete modeTokens[fromToken]
        replaceCount += 1
      }
      for (const [tokenName, tokenValue] of Object.entries(modeTokens)) {
        const updated = replaceTokenReferencesInText(tokenValue, fromToken, toToken)
        if (!updated.count) continue
        modeTokens[tokenName] = updated.text
        replaceCount += updated.count
      }
    }
  }

  const sourceUpdated = replaceTokenReferencesInText(sourceCode.value, fromToken, toToken)
  if (sourceUpdated.count) {
    sourceCode.value = sourceUpdated.text
    replaceCount += sourceUpdated.count
  }

  const rawCssUpdated = replaceTokenReferencesInText(rawCss.value, fromToken, toToken)
  if (rawCssUpdated.count) {
    rawCss.value = rawCssUpdated.text
    replaceCount += rawCssUpdated.count
  }

  const nextOverrides = { ...visualOverridesMap.value }
  for (const [selector, row] of Object.entries(nextOverrides || {})) {
    if (!row || typeof row !== 'object') continue
    const nextRow = { ...row, styles: { ...(row.styles || {}) } }
    let rowChanged = false
    for (const [styleKey, styleValue] of Object.entries(nextRow.styles || {})) {
      const replaced = replaceTokenReferencesInText(styleValue, fromToken, toToken)
      if (!replaced.count) continue
      nextRow.styles[styleKey] = replaced.text
      replaceCount += replaced.count
      rowChanged = true
    }
    if (nextRow.apply_html) {
      const htmlReplaced = replaceTokenReferencesInText(nextRow.html_content, fromToken, toToken)
      if (htmlReplaced.count) {
        nextRow.html_content = htmlReplaced.text
        replaceCount += htmlReplaced.count
        rowChanged = true
      }
    }
    if (nextRow.apply_text) {
      const textReplaced = replaceTokenReferencesInText(nextRow.text_content, fromToken, toToken)
      if (textReplaced.count) {
        nextRow.text_content = textReplaced.text
        replaceCount += textReplaced.count
        rowChanged = true
      }
    }
    if (rowChanged) nextOverrides[selector] = nextRow
  }
  visualOverridesMap.value = nextOverrides
  applyVisualOverridesToDocument(visualFrameDocument)
  tokenCollections.value = nextCollections
  applyActiveTokenModeToDocument(visualFrameDocument)
  collectPreviewCssVariables(visualFrameDocument)
  success.value = replaceCount > 0 ? `Bulk replace انجام شد (${replaceCount}).` : 'موردی برای جایگزینی پیدا نشد.'
  error.value = ''
}

function onTextParagraphPresetInput(value) {
  textParagraphPreset.value = String(value || 'body')
}

function onTextOpenTypeInput(value) {
  textOpenType.value = String(value || '')
}

function onTextLigaturesInput(value) {
  textLigatures.value = String(value || 'normal')
}

function onTextBaselineStepInput(value) {
  textBaselineStep.value = parsePositiveInt(value, textBaselineStep.value || 4, 64)
}

function onTextFindQueryInput(value) {
  textFindQuery.value = String(value || '')
}

function onTextReplaceValueInput(value) {
  textReplaceValue.value = String(value || '')
}

function onTextReplaceScopeInput(value) {
  const scope = String(value || '').trim().toLowerCase()
  textReplaceScope.value = scope === 'page' ? 'page' : 'selection'
}

function applyTextParagraphPreset() {
  const ids = getSelectedNodeIds()
  if (!ids.length) return
  const preset = textParagraphPresetOptions.find((row) => row.key === textParagraphPreset.value)
  if (!preset?.styles || typeof preset.styles !== 'object') return
  const styleEntries = Object.entries(preset.styles).map(([key, value]) => ({
    key: String(key || '').trim(),
    value: String(value ?? ''),
  }))
  if (!styleEntries.length) return
  const changed = applyStyleBatchForNodes(ids, styleEntries)
  if (!changed) return
  success.value = 'Paragraph style اعمال شد.'
  error.value = ''
  nextTick(() => { syncResizeOverlay(); syncRedlineOverlay() })
}

function applyTextListCommand(command) {
  const ids = getSelectedNodeIds()
  if (!ids.length) return
  const cmd = String(command || '').trim().toLowerCase()
  if (!cmd) return
  if (cmd === 'ul' || cmd === 'ol') {
    const listType = cmd === 'ul' ? 'disc' : 'decimal'
    const changed = applyStyleBatchForNodes(ids, [
      { key: 'display', value: 'list-item' },
      { key: 'listStyleType', value: listType },
      { key: 'listStylePosition', value: 'outside' },
    ])
    if (changed) {
      success.value = 'List style اعمال شد.'
      error.value = ''
    }
    return
  }
  if (cmd === 'indent' || cmd === 'outdent') {
    const delta = Math.max(2, Number(textBaselineStep.value || 4)) * (cmd === 'indent' ? 1 : -1)
    const changedEntries = []
    for (const nodeId of ids) {
      const element = getVisualElementById(nodeId)
      if (!element) continue
      const current = Number.parseFloat(String(element.style.textIndent || visualPreviewFrame.value?.contentWindow?.getComputedStyle?.(element)?.textIndent || '0')) || 0
      const next = Math.max(0, Math.round(current + delta))
      changedEntries.push({ nodeId, next })
    }
    if (!changedEntries.length) return
    for (const row of changedEntries) {
      applyStyleBatchForNodes([row.nodeId], [{ key: 'textIndent', value: `${row.next}px` }])
    }
    success.value = cmd === 'indent' ? 'Indent اعمال شد.' : 'Outdent اعمال شد.'
    error.value = ''
  }
}

function applyParagraphSpacing(value) {
  const ids = getSelectedNodeIds()
  if (!ids.length) return
  pushVisualHistorySnapshot({ force: true })
  const rawValue = String(value || '').trim()
  const normalizedValue = rawValue
    ? (rawValue.endsWith('px') || rawValue.endsWith('rem') || rawValue.endsWith('em') || rawValue.endsWith('%') ? rawValue : `${rawValue}px`)
    : ''
  const changed = applyStyleBatchForNodes(ids, [{ key: '--mysite-paragraph-spacing', value: normalizedValue }])
  if (!changed) return
  for (const nodeId of ids) {
    const element = getVisualElementById(nodeId)
    if (!element) continue
    if (String(element.tagName || '').toLowerCase() === 'p') {
      element.style.marginBottom = normalizedValue || ''
    } else {
      const paragraphs = Array.from(element.querySelectorAll('p'))
      for (const paragraph of paragraphs) paragraph.style.marginBottom = normalizedValue || ''
    }
  }
  if (visualSelectedElement) visualProps.value.paragraphSpacing = normalizedValue
  success.value = 'Paragraph spacing به‌روزرسانی شد.'
  error.value = ''
}

function applyInlineTextCommand(command) {
  const cmd = String(command || '').trim().toLowerCase()
  if (!cmd) return
  if (inlineTextEditState?.element && visualFrameDocument) {
    try {
      if (cmd === 'bold' || cmd === 'italic' || cmd === 'underline') visualFrameDocument.execCommand(cmd, false)
    } catch {
      // noop
    }
    inlineTextEditState.element.focus()
    return
  }
  if (cmd === 'bold') applyInlineStyleRun('fontWeight', '700')
  else if (cmd === 'italic') applyInlineStyleRun('fontStyle', 'italic')
  else if (cmd === 'underline') applyInlineStyleRun('textDecoration', 'underline')
}

function applyInlineStyleRun(styleKey, styleValue) {
  const key = String(styleKey || '').trim()
  if (!key) return
  const value = String(styleValue ?? '').trim()
  if (inlineTextEditState?.element) {
    applyInlineStyleToSelection(key, value || 'inherit')
    rawHtmlInput.value = String(inlineTextEditState.element.innerHTML || '')
    syncVisualPropsFromElement(inlineTextEditState.element)
    success.value = 'Style run اعمال شد.'
    error.value = ''
    return
  }
  const ids = getSelectedNodeIds()
  if (!ids.length) return
  pushVisualHistorySnapshot({ force: true })
  const changed = applyStyleBatchForNodes(ids, [{ key, value }])
  if (!changed) return
  success.value = 'Text style اعمال شد.'
  error.value = ''
}

const SHARED_TEXT_STYLE_FIELDS = ['fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'letterSpacing', 'textAlign', 'color']

function captureTypographyStyleSnapshot(element) {
  if (!element) return {}
  const computed = visualPreviewFrame.value?.contentWindow?.getComputedStyle?.(element)
  const output = {}
  for (const key of SHARED_TEXT_STYLE_FIELDS) {
    const value = String(element.style?.[key] || computed?.[key] || '').trim()
    if (!value) continue
    output[key] = value
  }
  const paragraphSpacing = String(element.style?.getPropertyValue?.('--mysite-paragraph-spacing') || computed?.getPropertyValue?.('--mysite-paragraph-spacing') || '').trim()
  if (paragraphSpacing) output['--mysite-paragraph-spacing'] = paragraphSpacing
  return output
}

function applySharedTextStyle(styleId) {
  const id = String(styleId || '').trim()
  const styleRow = id ? sharedTextStyles.value?.[id] : null
  if (!styleRow?.styles) return false
  const ids = getSelectedNodeIds()
  if (!ids.length) return false
  pushVisualHistorySnapshot({ force: true })
  const styleEntries = Object.entries(styleRow.styles || {}).map(([key, value]) => ({ key: String(key || '').trim(), value: String(value || '') })).filter((row) => row.key)
  if (!styleEntries.length) return false
  const changed = applyStyleBatchForNodes(ids, styleEntries)
  if (!changed) return false
  for (const nodeId of ids) {
    const element = getVisualElementById(nodeId)
    if (element) element.setAttribute(TEXT_STYLE_LINK_ATTR, id)
  }
  success.value = `Shared style "${styleRow.name || id}" اعمال شد.`
  error.value = ''
  return true
}

function detachSharedTextStyleFromSelection() {
  const ids = getSelectedNodeIds()
  if (!ids.length) return false
  pushVisualHistorySnapshot({ force: true })
  let detached = 0
  for (const nodeId of ids) {
    const element = getVisualElementById(nodeId)
    if (!element) continue
    if (!element.hasAttribute(TEXT_STYLE_LINK_ATTR)) continue
    element.removeAttribute(TEXT_STYLE_LINK_ATTR)
    detached += 1
  }
  if (!detached) return false
  success.value = 'Shared text style detached شد.'
  error.value = ''
  return true
}

function updateSharedTextStyleFromSelection(styleId = '') {
  const targetId = String(styleId || selectedSharedTextStyleId.value || '').trim()
  if (!targetId) return false
  if (!visualSelectedElement) return false
  const snapshot = captureTypographyStyleSnapshot(visualSelectedElement)
  if (!Object.keys(snapshot).length) return false
  const next = normalizeSharedTextStyles({
    ...(sharedTextStyles.value || {}),
    [targetId]: {
      id: targetId,
      name: String(sharedTextStyles.value?.[targetId]?.name || targetId),
      styles: snapshot,
    },
  })
  sharedTextStyles.value = next
  success.value = `Shared style "${targetId}" به‌روزرسانی شد.`
  error.value = ''
  return true
}

function applyTextOpenTypeSettings() {
  const ids = getSelectedNodeIds()
  if (!ids.length) return
  const styleEntries = []
  const openType = String(textOpenType.value || '').trim()
  const ligatures = String(textLigatures.value || '').trim()
  if (openType) styleEntries.push({ key: 'fontFeatureSettings', value: openType })
  if (ligatures) styleEntries.push({ key: 'fontVariantLigatures', value: ligatures })
  if (!styleEntries.length) return
  const changed = applyStyleBatchForNodes(ids, styleEntries)
  if (!changed) return
  success.value = 'OpenType تنظیم شد.'
  error.value = ''
}

function resolveLineHeightPx(element) {
  if (!element) return 0
  const frameWindow = visualPreviewFrame.value?.contentWindow
  const computed = frameWindow?.getComputedStyle?.(element)
  const fontSize = Number.parseFloat(String(element.style.fontSize || computed?.fontSize || '16')) || 16
  const lineHeightRaw = String(element.style.lineHeight || computed?.lineHeight || 'normal').trim().toLowerCase()
  if (!lineHeightRaw || lineHeightRaw === 'normal') return fontSize * 1.35
  if (lineHeightRaw.endsWith('px')) return Number.parseFloat(lineHeightRaw) || (fontSize * 1.35)
  const asNumber = Number.parseFloat(lineHeightRaw)
  if (!Number.isFinite(asNumber)) return fontSize * 1.35
  if (lineHeightRaw.endsWith('rem')) return asNumber * 16
  if (lineHeightRaw.endsWith('em')) return asNumber * fontSize
  return asNumber > 6 ? asNumber : asNumber * fontSize
}

function snapSelectedTextToBaseline() {
  const ids = getSelectedNodeIds()
  if (!ids.length) return
  const step = Math.max(2, Number(textBaselineStep.value || 4))
  let changed = 0
  for (const nodeId of ids) {
    const element = getVisualElementById(nodeId)
    if (!element) continue
    const lineHeightPx = resolveLineHeightPx(element)
    const snapped = Math.max(step, Math.ceil(lineHeightPx / step) * step)
    if (applyStyleBatchForNodes([nodeId], [{ key: 'lineHeight', value: `${snapped}px` }])) changed += 1
  }
  if (!changed) return
  success.value = `Baseline snap اعمال شد (${changed}).`
  error.value = ''
}

function replaceTextInElementNodes(element, searchTerm, replacementValue) {
  const target = element && element.nodeType === 1 ? element : null
  if (!target) return 0
  const query = String(searchTerm || '')
  if (!query) return 0
  const replacement = String(replacementValue || '')
  const escaped = escapeRegex(query)
  if (!escaped) return 0
  const regex = new RegExp(escaped, 'g')
  const doc = target.ownerDocument
  const frameWindow = visualPreviewFrame.value?.contentWindow
  const nodeFilter = frameWindow?.NodeFilter || window.NodeFilter
  const walker = doc.createTreeWalker(target, nodeFilter.SHOW_TEXT)
  let textNode = walker.nextNode()
  let replacedCount = 0
  while (textNode) {
    const text = String(textNode.nodeValue || '')
    if (text && regex.test(text)) {
      regex.lastIndex = 0
      const matches = text.match(regex)
      if (matches?.length) replacedCount += matches.length
      textNode.nodeValue = text.replace(regex, replacement)
    }
    regex.lastIndex = 0
    textNode = walker.nextNode()
  }
  return replacedCount
}

function pickEditableOwnerForTextNode(node) {
  let current = node?.parentElement || null
  while (current) {
    if (isVisualEditableElement(current)) return current
    current = current.parentElement
  }
  return null
}

function topLevelElements(elements) {
  const rows = Array.isArray(elements) ? elements.filter(Boolean) : []
  return rows.filter((element) => !rows.some((other) => other !== element && other.contains(element)))
}

function applyTextFindReplace() {
  const query = String(textFindQuery.value || '')
  if (!query) return
  const scope = String(textReplaceScope.value || 'selection').trim().toLowerCase()
  const changedElements = new Set()
  const queryRegex = new RegExp(escapeRegex(query), 'g')

  pushVisualHistorySnapshot({ force: true })
  let replaceCount = 0
  if (scope === 'page') {
    if (!visualFrameDocument?.body) return
    const nodeFilter = visualPreviewFrame.value?.contentWindow?.NodeFilter || window.NodeFilter
    const walker = visualFrameDocument.createTreeWalker(visualFrameDocument.body, nodeFilter.SHOW_TEXT)
    let textNode = walker.nextNode()
    while (textNode) {
      const text = String(textNode.nodeValue || '')
      if (text && queryRegex.test(text)) {
        queryRegex.lastIndex = 0
        const matches = text.match(queryRegex)
        if (matches?.length) replaceCount += matches.length
        textNode.nodeValue = text.replace(queryRegex, String(textReplaceValue.value || ''))
        const owner = pickEditableOwnerForTextNode(textNode)
        if (owner) changedElements.add(owner)
      }
      queryRegex.lastIndex = 0
      textNode = walker.nextNode()
    }
  } else {
    const selectedTargets = topLevelElements(getSelectedElementsInDomOrder())
    for (const element of selectedTargets) {
      const changed = replaceTextInElementNodes(element, query, textReplaceValue.value)
      if (!changed) continue
      replaceCount += changed
      changedElements.add(element)
    }
  }

  if (!replaceCount) {
    success.value = 'موردی برای جایگزینی پیدا نشد.'
    error.value = ''
    return
  }

  const map = { ...visualOverridesMap.value }
  let touchedLayers = 0
  for (const element of Array.from(changedElements)) {
    const nodeId = ensureVisualNodeId(element)
    if (!visualLayerIndex.value[nodeId]) upsertSingleLayerForElement(element)
    const selector = ensureLayerSelector(nodeId, element)
    const layer = visualLayerIndex.value?.[nodeId]
    if (!selector) continue
    const row = map[selector]
      ? { ...map[selector], styles: { ...(map[selector].styles || {}) } }
      : { selector, tag: layer?.tag || '', label: layer?.label || '', styles: {}, apply_text: false, text_content: '', apply_html: false, html_content: '' }
    const html = String(element.innerHTML || '')
    if (html.trim()) {
      row.apply_html = true
      row.html_content = html
      row.apply_text = false
      row.text_content = ''
    } else {
      row.apply_html = false
      row.html_content = ''
      row.apply_text = true
      row.text_content = String(element.textContent || '')
    }
    if (!row.apply_text && !row.apply_html && !Object.keys(row.styles || {}).length) delete map[selector]
    else map[selector] = row
    touchedLayers += 1
  }
  visualOverridesMap.value = map
  if (visualSelectedElement) rawHtmlInput.value = String(visualSelectedElement.innerHTML || '')
  syncVisualPropsFromElement(visualSelectedElement)
  success.value = `جایگزینی متن انجام شد (${replaceCount}).`
  error.value = ''
  if (scope === 'page' && touchedLayers > 0) {
    void runVisualLayerScan(visualFrameDocument, { loadToken: previewFrameLoadToken, focusNodeId: visualSelectedId.value })
  }
}

const presetAssetItems = [
  { id: '__preset-frame', name: 'Frame Preset', type: 'component', source: 'preset', tool: 'frame', description: 'Canvas frame block' },
  { id: '__preset-rect', name: 'Rectangle Preset', type: 'component', source: 'preset', tool: 'rectangle', description: 'Primitive shape' },
  { id: '__preset-text', name: 'Text Preset', type: 'component', source: 'preset', tool: 'text', description: 'Text layer starter' },
  { id: '__preset-comment', name: 'Comment Preset', type: 'component', source: 'preset', tool: 'comment', description: 'Comment sticky block' },
]

const styleAssetItems = computed(() => {
  const base = [
    {
      id: '__style-surface-card',
      name: 'Surface/Card',
      type: 'style',
      styleEntries: [
        { key: 'backgroundColor', value: '#ffffff' },
        { key: 'borderRadius', value: '12px' },
        { key: 'borderColor', value: '#d0d7e2' },
        { key: 'borderWidth', value: '1px' },
        { key: 'padding', value: '16px' },
      ],
      description: 'Card surface',
    },
    {
      id: '__style-text-heading',
      name: 'Text/Heading',
      type: 'style',
      styleEntries: [
        { key: 'fontSize', value: '32px' },
        { key: 'fontWeight', value: '700' },
        { key: 'lineHeight', value: '1.3' },
      ],
      description: 'Heading typography',
    },
    {
      id: '__style-text-body',
      name: 'Text/Body',
      type: 'style',
      styleEntries: [
        { key: 'fontSize', value: '16px' },
        { key: 'fontWeight', value: '400' },
        { key: 'lineHeight', value: '1.7' },
      ],
      description: 'Body typography',
    },
  ]
  for (const token of textStyleTokens.value || []) {
    const tokenName = String(token?.name || '').trim()
    if (!tokenName) continue
    const safe = tokenName.replace(/[^a-z0-9_-]/gi, '-').toLowerCase()
    base.push({
      id: `__style-token-${safe}`,
      name: `Style/${tokenName}`,
      type: 'style',
      styleEntries: [{ key: 'fontFamily', value: `var(${tokenName})` }],
      description: 'From CSS variable',
    })
  }
  return base
})

const tokenAssetItems = computed(() =>
  (Array.isArray(cssVariables.value) ? cssVariables.value : []).map((row) => {
    const tokenName = String(row?.name || '').trim()
    const safe = tokenName.replace(/[^a-z0-9_-]/gi, '-').toLowerCase()
    return {
      id: `__token-${safe}`,
      name: tokenName,
      type: 'token',
      tokenName,
      tokenValue: String(row?.value || '').trim(),
      description: String(row?.value || '').trim(),
    }
  })
)

function normalizeImageAssetUrl(value) {
  const raw = String(value || '').trim()
  if (!raw) return ''
  if (/^(data:|blob:|https?:\/\/)/i.test(raw)) return raw
  if (raw.startsWith('//')) return `https:${raw}`
  return raw.startsWith('/') ? raw : `/${raw}`
}

function isImageAssetUrl(value) {
  const raw = String(value || '').trim()
  if (!raw) return false
  if (/^(data:image\/|blob:)/i.test(raw)) return true
  const clean = raw.split('?')[0].split('#')[0]
  return /\.(avif|webp|png|jpe?g|gif|svg|bmp|ico)$/i.test(clean)
}

function fileNameFromUrl(value) {
  const raw = String(value || '').trim()
  if (!raw) return 'image'
  const clean = raw.split('?')[0].split('#')[0]
  const last = clean.slice(clean.lastIndexOf('/') + 1)
  return last || 'image'
}

function mapFileRowToImageAsset(row) {
  const fileUrl = normalizeImageAssetUrl(row?.file_url || row?.fileUrl || '')
  if (!fileUrl || !isImageAssetUrl(fileUrl)) return null
  const fileName = String(row?.file_name || row?.fileName || fileNameFromUrl(fileUrl) || 'image').trim() || 'image'
  const fileId = String(row?.name || '').trim() || `file-${fileName}`
  return {
    id: `__image-${fileId}`,
    fileId,
    name: fileName,
    url: fileUrl,
    previewUrl: fileUrl,
    type: 'image',
    description: fileUrl,
  }
}

const filteredImageLibraryItems = computed(() => {
  const rows = Array.isArray(imageLibraryItems.value) ? imageLibraryItems.value : []
  const query = String(imageAssetQuery.value || '').trim().toLowerCase()
  if (!query) return rows
  return rows.filter((row) => {
    const name = String(row?.name || '').toLowerCase()
    const url = String(row?.url || '').toLowerCase()
    return name.includes(query) || url.includes(query)
  })
})

const selectedImageTargetType = computed(() => {
  const tag = String(visualSelectedLayer.value?.tag || '').trim().toLowerCase()
  if (tag === 'img') return 'img'
  if (tag === 'picture') return 'picture'
  if (tag === 'source') return 'source'
  return 'background'
})

function parseCssImageUrl(value) {
  const raw = String(value || '').trim()
  if (!raw || raw === 'none') return ''
  const match = raw.match(/url\((['"]?)(.*?)\1\)/i)
  return match ? String(match[2] || '').trim() : raw
}

const selectedImageSource = computed(() => {
  const activeId = String(visualSelectedId.value || '').trim()
  const element = activeId ? getVisualElementById(activeId) : visualSelectedElement
  if (!element) return ''
  const tag = String(element.tagName || '').toLowerCase()
  if (tag === 'img') return String(element.getAttribute('src') || '').trim()
  if (tag === 'source') return String(element.getAttribute('srcset') || element.getAttribute('src') || '').trim()
  if (tag === 'picture') {
    const innerImg = element.querySelector('img')
    if (innerImg) return String(innerImg.getAttribute('src') || '').trim()
  }
  const inline = parseCssImageUrl(element.style?.backgroundImage || '')
  if (inline) return inline
  try {
    const computed = visualPreviewFrame.value?.contentWindow?.getComputedStyle?.(element)
    return parseCssImageUrl(computed?.backgroundImage || '')
  } catch {
    return ''
  }
})

const filteredAssetItems = computed(() => {
  const rows = [
    ...presetAssetItems,
    ...componentLibraryItems.value.map((row) => ({ ...row, type: 'component', source: 'library', description: 'Reusable component' })),
    ...styleAssetItems.value,
    ...tokenAssetItems.value,
    ...filteredImageLibraryItems.value,
  ]
  const query = String(assetQuery.value || '').trim().toLowerCase()
  if (!query) return rows
  return rows.filter((row) => {
    const name = String(row?.name || '').toLowerCase()
    const description = String(row?.description || '').toLowerCase()
    return name.includes(query) || description.includes(query)
  })
})

const selectedComponentRecord = computed(() => {
  const componentId = String(selectedComponentId.value || '').trim()
  if (!componentId) return null
  return componentLibrary.value?.[componentId] || null
})

const selectedComponentVariants = computed(() => {
  const record = selectedComponentRecord.value
  if (!record?.variants || typeof record.variants !== 'object') return []
  return Object.keys(record.variants)
})

const selectedComponentVariant = computed(() => {
  if (!visualSelectedElement) return 'default'
  return String(visualSelectedElement.getAttribute(COMPONENT_VARIANT_ATTR) || 'default').trim() || 'default'
})

const selectedVariantPropertyRows = computed(() => {
  const variants = Array.isArray(selectedComponentVariants.value) ? selectedComponentVariants.value : []
  if (!variants.length) return []
  const valuesByKey = {}
  const parse = (variantKey) => {
    const text = String(variantKey || '').trim()
    if (!text) return {}
    if (!text.includes('=')) return { state: text }
    const out = {}
    for (const token of text.split(',')) {
      const [rawKey, ...rest] = token.split('=')
      const key = String(rawKey || '').trim()
      const value = String(rest.join('=') || '').trim()
      if (!key || !value) continue
      out[key] = value
    }
    return out
  }
  for (const variantKey of variants) {
    const map = parse(variantKey)
    for (const [key, value] of Object.entries(map)) {
      if (!valuesByKey[key]) valuesByKey[key] = new Set()
      valuesByKey[key].add(value)
    }
  }
  const currentMap = parse(selectedComponentVariant.value)
  return Object.entries(valuesByKey).map(([key, valueSet]) => ({
    key,
    value: String(currentMap[key] || ''),
    options: Array.from(valueSet).sort((a, b) => a.localeCompare(b)),
  }))
})

const selectedNestedComponentInstances = computed(() => {
  if (!visualSelectedElement) return []
  const result = []
  const nested = Array.from(visualSelectedElement.querySelectorAll(`[${COMPONENT_INSTANCE_ATTR}]`))
  for (const element of nested) {
    if (!isVisualEditableElement(element)) continue
    const nodeId = ensureVisualNodeId(element)
    if (!nodeId || nodeId === visualSelectedId.value) continue
    const componentId = String(element.getAttribute(COMPONENT_INSTANCE_ATTR) || '').trim()
    if (!componentId) continue
    const variant = String(element.getAttribute(COMPONENT_VARIANT_ATTR) || 'default').trim() || 'default'
    result.push({
      nodeId,
      componentId,
      variant,
      label: nodeLabel(element),
    })
  }
  return result.slice(0, 40)
})

function extractTokenRefsFromText(text) {
  const refs = new Set()
  const source = String(text || '')
  if (!source) return []
  const matches = source.match(/var\(\s*(--[A-Za-z0-9_-]+)\s*\)/g) || []
  for (const match of matches) {
    const token = String(match || '').match(/--[A-Za-z0-9_-]+/)
    if (token?.[0]) refs.add(token[0])
  }
  return Array.from(refs)
}

const handoffInspect = computed(() => {
  if (!visualSelectedElement) return null
  const layer = visualSelectedLayer.value
  const selector = String(layer?.selector || '').trim()
  const row = selector ? visualOverridesMap.value?.[selector] : null
  const win = visualPreviewFrame.value?.contentWindow
  const computedStyle = win?.getComputedStyle ? win.getComputedStyle(visualSelectedElement) : null
  const rect = visualSelectedElement.getBoundingClientRect()
  const scrollX = Number(win?.scrollX || 0)
  const scrollY = Number(win?.scrollY || 0)
  const styleTokens = new Set()
  for (const value of Object.values(row?.styles || {})) {
    for (const token of extractTokenRefsFromText(value)) styleTokens.add(token)
  }
  if (row?.apply_html) {
    for (const token of extractTokenRefsFromText(row.html_content)) styleTokens.add(token)
  }
  const componentId = String(visualSelectedElement.getAttribute(COMPONENT_INSTANCE_ATTR) || '').trim()
  const variant = String(visualSelectedElement.getAttribute(COMPONENT_VARIANT_ATTR) || 'default').trim() || 'default'
  return {
    selector,
    tag: String(layer?.tag || visualSelectedElement.tagName || '').toLowerCase(),
    box: {
      x: Math.round(rect.left + scrollX),
      y: Math.round(rect.top + scrollY),
      width: Math.round(rect.width),
      height: Math.round(rect.height),
    },
    margin: `${computedStyle?.marginTop || '0'} ${computedStyle?.marginRight || '0'} ${computedStyle?.marginBottom || '0'} ${computedStyle?.marginLeft || '0'}`,
    padding: `${computedStyle?.paddingTop || '0'} ${computedStyle?.paddingRight || '0'} ${computedStyle?.paddingBottom || '0'} ${computedStyle?.paddingLeft || '0'}`,
    typography: [
      computedStyle?.fontFamily || '',
      computedStyle?.fontSize || '',
      computedStyle?.fontWeight || '',
      computedStyle?.lineHeight || '',
    ].filter(Boolean).join(' / '),
    component: componentId ? `${componentId} (${variant})` : 'none',
    tokens: Array.from(styleTokens).sort((a, b) => a.localeCompare(b)),
  }
})

function computeElementBoxForHandoff(element) {
  if (!element) return null
  const win = visualPreviewFrame.value?.contentWindow
  const rect = element.getBoundingClientRect()
  const scrollX = Number(win?.scrollX || 0)
  const scrollY = Number(win?.scrollY || 0)
  return {
    left: Math.round(rect.left + scrollX),
    top: Math.round(rect.top + scrollY),
    width: Math.round(rect.width),
    height: Math.round(rect.height),
    right: Math.round(rect.left + scrollX + rect.width),
    bottom: Math.round(rect.top + scrollY + rect.height),
    centerX: Math.round(rect.left + scrollX + (rect.width / 2)),
    centerY: Math.round(rect.top + scrollY + (rect.height / 2)),
  }
}

function computeConstraintSnapshot(element) {
  if (!element) return { horizontal: 'left', vertical: 'top', size: 'fixed', sizeWidth: 'fixed', sizeHeight: 'fixed' }
  const size = String(element.getAttribute(CONSTRAINT_SIZE_ATTR) || 'fixed')
  return {
    horizontal: String(element.getAttribute(CONSTRAINT_H_ATTR) || 'left'),
    vertical: String(element.getAttribute(CONSTRAINT_V_ATTR) || 'top'),
    size,
    sizeWidth: String(element.getAttribute(CONSTRAINT_SIZE_W_ATTR) || size || 'fixed'),
    sizeHeight: String(element.getAttribute(CONSTRAINT_SIZE_H_ATTR) || size || 'fixed'),
  }
}

const handoffRedline = computed(() => {
  const selectedIds = Array.isArray(visualSelectedIds.value) ? visualSelectedIds.value.filter(Boolean) : []
  if (selectedIds.length !== 2) return null
  const firstElement = getVisualElementById(selectedIds[0])
  const secondElement = getVisualElementById(selectedIds[1])
  if (!firstElement || !secondElement) return null
  const boxA = computeElementBoxForHandoff(firstElement)
  const boxB = computeElementBoxForHandoff(secondElement)
  if (!boxA || !boxB) return null

  const deltaX = boxB.left - boxA.left
  const deltaY = boxB.top - boxA.top
  let gapX = 0
  if (boxA.right < boxB.left) gapX = boxB.left - boxA.right
  else if (boxB.right < boxA.left) gapX = boxA.left - boxB.right
  let gapY = 0
  if (boxA.bottom < boxB.top) gapY = boxB.top - boxA.bottom
  else if (boxB.bottom < boxA.top) gapY = boxA.top - boxB.bottom
  const centerDistance = Math.sqrt(((boxB.centerX - boxA.centerX) ** 2) + ((boxB.centerY - boxA.centerY) ** 2))

  const threshold = 1
  const matched = []
  if (Math.abs(boxA.left - boxB.left) <= threshold) matched.push('left')
  if (Math.abs(boxA.right - boxB.right) <= threshold) matched.push('right')
  if (Math.abs(boxA.top - boxB.top) <= threshold) matched.push('top')
  if (Math.abs(boxA.bottom - boxB.bottom) <= threshold) matched.push('bottom')
  if (Math.abs(boxA.centerX - boxB.centerX) <= threshold) matched.push('center-x')
  if (Math.abs(boxA.centerY - boxB.centerY) <= threshold) matched.push('center-y')

  const layerA = visualLayerIndex.value?.[selectedIds[0]]
  const layerB = visualLayerIndex.value?.[selectedIds[1]]

  return {
    node_a: {
      id: selectedIds[0],
      selector: String(layerA?.selector || ''),
      label: String(layerA?.label || nodeLabel(firstElement)),
      box: boxA,
      constraints: computeConstraintSnapshot(firstElement),
    },
    node_b: {
      id: selectedIds[1],
      selector: String(layerB?.selector || ''),
      label: String(layerB?.label || nodeLabel(secondElement)),
      box: boxB,
      constraints: computeConstraintSnapshot(secondElement),
    },
    delta: { x: Math.round(deltaX), y: Math.round(deltaY) },
    gap: { x: Math.round(gapX), y: Math.round(gapY) },
    center_distance: Math.round(centerDistance),
    alignment: { matched },
  }
})

const {
  snippetTab,
  cssSnippet,
  htmlSnippet,
  vueSnippet,
  reactSnippet,
  swiftuiSnippet,
  composeSnippet,
  tokenSnippet,
  redlineSnippet,
  fullSourcePreview,
  rawCssPreview,
} = useDeveloperCodeView({
  visualSelectedLayer,
  visualOverridesMap,
  sourceCode,
  rawCss,
  handoffInspect,
  handoffRedline,
  selectedConstraintState,
})

function onSnippetTabChange(value) {
  snippetTab.value = String(value || 'css')
}

function onLayerQueryInput(value) {
  visualLayerQuery.value = String(value || '')
}

function onAssetQueryInput(value) {
  assetQuery.value = String(value || '')
}

function onImageAssetQueryInput(value) {
  imageAssetQuery.value = String(value || '')
}

async function refreshImageAssetLibrary(options = {}) {
  if (imageLibraryLoading.value && !options?.force) return false
  imageLibraryLoading.value = true
  try {
    const query = String(options?.query ?? imageAssetQuery.value ?? '').trim()
    const filters = [
      ['is_folder', '=', 0],
      ['file_url', 'is', 'set'],
    ]
    if (query) filters.push(['file_name', 'like', `%${query}%`])
    const { response, payload } = await postEditorMethodWithFallback('/api/method/frappe.client.get_list', {
      doctype: 'File',
      fields: ['name', 'file_name', 'file_url', 'modified'],
      filters,
      order_by: 'modified desc',
      limit_page_length: 80,
    })
    if (!response.ok || payload?.exception || payload?.exc_type) {
      throw new Error(payload?.message || 'دریافت لیست تصاویر سیستم ناموفق بود.')
    }
    const rows = Array.isArray(payload?.message) ? payload.message : (Array.isArray(payload?.data) ? payload.data : [])
    imageLibraryItems.value = rows.map(mapFileRowToImageAsset).filter(Boolean)
    return true
  } catch (err) {
    if (!options?.silentError) error.value = err?.message || 'خطا در دریافت تصاویر سیستم.'
    return false
  } finally {
    imageLibraryLoading.value = false
  }
}

async function uploadImageAssetFromFile(file, options = {}) {
  const imageFile = file instanceof File ? file : null
  if (!imageFile) return false
  if (!String(imageFile.type || '').toLowerCase().startsWith('image/')) {
    error.value = 'فقط فایل تصویر قابل آپلود است.'
    return false
  }
  imageUploadInProgress.value = true
  error.value = ''
  try {
    const formData = new FormData()
    formData.append('file', imageFile, imageFile.name || 'image')
    formData.append('is_private', '0')
    formData.append('folder', 'Home/Attachments')
    const headers = { 'X-Requested-With': 'XMLHttpRequest' }
    const csrfToken = resolveCsrfToken()
    if (csrfToken) headers['X-Frappe-CSRF-Token'] = csrfToken
    const response = await fetch('/api/method/upload_file', {
      method: 'POST',
      credentials: 'same-origin',
      headers,
      body: formData,
    })
    const payload = await parseJsonResponse(response)
    if (!response.ok || payload?.exception || payload?.exc_type) {
      throw new Error(payload?.message || 'آپلود تصویر ناموفق بود.')
    }
    const message = payload?.message || payload || {}
    const uploadedUrl = normalizeImageAssetUrl(
      message?.file_url || message?.fileUrl || message?.file?.file_url || message?.file?.fileUrl || ''
    )
    if (!uploadedUrl) throw new Error('آدرس فایل آپلود شده از سرور دریافت نشد.')
    await refreshImageAssetLibrary({ force: true, silentError: true })
    const applyToSelection = options?.applyToSelection !== false
    const applied = applyToSelection ? applyImageSourceToSelection(uploadedUrl, { silentSuccess: true }) : false
    if (applied) success.value = 'تصویر آپلود و روی المنت انتخابی اعمال شد.'
    else success.value = 'تصویر آپلود شد و به Assets اضافه شد.'
    error.value = ''
    return true
  } catch (err) {
    error.value = err?.message || 'خطا در آپلود تصویر.'
    return false
  } finally {
    imageUploadInProgress.value = false
  }
}

function applyImageAssetItem(asset, options = {}) {
  const imageUrl = normalizeImageAssetUrl(asset?.url || asset?.file_url || asset?.fileUrl || '')
  if (!imageUrl) return false
  const point = options?.point && Number.isFinite(Number(options?.point?.x)) && Number.isFinite(Number(options?.point?.y))
    ? { x: Number(options.point.x), y: Number(options.point.y) }
    : null
  const applied = applyImageSourceToSelection(imageUrl, { silentSuccess: true })
  if (applied) {
    success.value = 'تصویر روی المنت انتخابی اعمال شد.'
    error.value = ''
    return true
  }
  if (!visualFrameDocument?.body) return false
  createImageElementAtPoint(imageUrl, point || { x: 120, y: 120 })
  return true
}

function onAssetDragStart(asset) {
  draggingAssetItem.value = asset && typeof asset === 'object' ? { ...asset } : null
}

function onAssetDragEnd() {
  draggingAssetItem.value = null
}

function parsePositiveInt(value, fallback = 1, max = 999) {
  const parsed = Number.parseInt(String(value ?? '').trim(), 10)
  if (!Number.isFinite(parsed)) return fallback
  return Math.min(Math.max(parsed, 1), Math.max(1, Number(max || 999)))
}

function onGridSizeInput(value) {
  gridSize.value = parsePositiveInt(value, gridSize.value || 8, 256)
}

function onLayoutGridColumnsInput(value) {
  layoutGridColumns.value = parsePositiveInt(value, layoutGridColumns.value || 12, 32)
}

function onNudgeStepInput(value) {
  nudgeStep.value = parsePositiveInt(value, nudgeStep.value || 1, 200)
}

function onNudgeStepLargeInput(value) {
  nudgeStepLarge.value = parsePositiveInt(value, nudgeStepLarge.value || 10, 400)
}

function onLayerSelect(payload) {
  if (payload && typeof payload === 'object') {
    selectVisualLayer(payload.id, {
      additive: payload.additive,
      toggle: payload.toggle,
      range: payload.range,
      rangeIds: payload.rangeIds,
    })
    return
  }
  selectVisualLayer(payload)
}

async function onEditorPageSelect(pageId) {
  const id = String(pageId || '').trim()
  if (!id) return
  const isFile = id.startsWith('file:')
  const nextRoute = isFile ? '' : normalizeEditorRoute(id)
  const nextFile = isFile ? String(id.slice(5) || '').trim() : ''
  if (!nextRoute && !nextFile) return
  if (!confirmDiscardChanges()) return

  const hadPreview = previewInitialized.value
  if (nextRoute) {
    route.value = nextRoute
    selectedTargetFile.value = ''
  } else {
    route.value = ''
    selectedTargetFile.value = nextFile
  }

  const params = new URLSearchParams(window.location.search)
  if (route.value) params.set('route', route.value)
  else params.delete('route')
  if (selectedTargetFile.value) params.set('target_file', selectedTargetFile.value)
  else params.delete('target_file')
  window.history.replaceState({}, '', `${window.location.pathname}?${params.toString()}`)

  await loadEditorPayload()
  if (hadPreview) await requestPreviewLoad()
}

async function copyTextToClipboard(value) {
  const text = String(value || '').trim()
  if (!text) return false
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
      return true
    }
  } catch {
    // fallback below
  }
  try {
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    textarea.style.pointerEvents = 'none'
    document.body.appendChild(textarea)
    textarea.focus()
    textarea.select()
    const ok = document.execCommand('copy')
    document.body.removeChild(textarea)
    return Boolean(ok)
  } catch {
    return false
  }
}

async function onLayerContextAction(payload) {
  const action = String(payload?.action || '').trim().toLowerCase()
  const nodeId = String(payload?.id || '').trim()
  if (!action || !nodeId) return
  if (!visualLayerIndex.value?.[nodeId]) return

  if (action === 'duplicate') {
    selectVisualLayer(nodeId)
    duplicateSelectedElement()
    return
  }
  if (action === 'delete') {
    selectVisualLayer(nodeId)
    await deleteSelectedElement()
    return
  }
  if (action === 'copy-selector') {
    const selector = String(visualLayerIndex.value?.[nodeId]?.selector || '').trim()
    if (!selector) return
    const copied = await copyTextToClipboard(selector)
    if (copied) {
      success.value = 'Selector کپی شد.'
      error.value = ''
    } else {
      error.value = 'دسترسی کپی در مرورگر مسدود است.'
    }
    return
  }
}

function onSaveNoteInput(value) {
  saveNote.value = String(value || '')
}

function onInspectorStyleQueryInput(value) {
  inspectorStyleQuery.value = String(value || '')
}

function onRawStylePropertyQueryInput(value) {
  rawStylePropertyQuery.value = String(value || '')
}

function onRawStyleDraftUpdate(value) {
  if (!value || typeof value !== 'object') return
  rawStyleDraft.value = { ...rawStyleDraft.value, ...value }
}

function onRawHtmlInput(value) {
  rawHtmlInput.value = String(value || '')
}

function onComponentVariantDraftInput(value) {
  componentVariantDraft.value = String(value || 'state')
}

function onComponentSwapTargetInput(value) {
  componentSwapTarget.value = String(value || '').trim()
}

function parseVariantKeyMap(variantKey) {
  const text = String(variantKey || '').trim()
  if (!text) return {}
  if (!text.includes('=')) return { state: text }
  const out = {}
  for (const token of text.split(',')) {
    const [rawKey, ...rest] = token.split('=')
    const key = String(rawKey || '').trim()
    const value = String(rest.join('=') || '').trim()
    if (!key || !value) continue
    out[key] = value
  }
  return out
}

function buildVariantKeyFromMap(map) {
  const entries = Object.entries(map || {})
    .filter(([key, value]) => String(key || '').trim() && String(value || '').trim())
    .map(([key, value]) => [String(key).trim(), String(value).trim()])
    .sort(([a], [b]) => a.localeCompare(b))
  if (!entries.length) return ''
  if (entries.length === 1 && entries[0][0] === 'state') return entries[0][1]
  return entries.map(([key, value]) => `${key}=${value}`).join(',')
}

async function onVariantPropertyChange(propKey, propValue) {
  const key = String(propKey || '').trim()
  const value = String(propValue || '').trim()
  if (!key) return
  const baseMap = parseVariantKeyMap(selectedComponentVariant.value)
  if (value) baseMap[key] = value
  else delete baseMap[key]
  const targetVariant = buildVariantKeyFromMap(baseMap)
  if (!targetVariant) return
  const variants = Array.isArray(selectedComponentVariants.value) ? selectedComponentVariants.value : []
  if (!variants.includes(targetVariant)) return
  await applyVariantToSelection(targetVariant)
}

function resolveCanvasDropPoint(payload) {
  const clientX = Number(payload?.clientX || 0)
  const clientY = Number(payload?.clientY || 0)
  const frameRect = visualPreviewFrame.value?.getBoundingClientRect?.()
  if (!frameRect) return { x: 120, y: 120 }
  const frameWindow = visualPreviewFrame.value?.contentWindow
  const scrollX = Number(frameWindow?.scrollX || 0)
  const scrollY = Number(frameWindow?.scrollY || 0)
  const zoom = Math.max(0.01, Number(canvasZoom.value || 1))
  const x = Math.max(0, Math.round(((clientX - frameRect.left) + scrollX) / zoom))
  const y = Math.max(0, Math.round(((clientY - frameRect.top) + scrollY) / zoom))
  return { x, y }
}

function resolveAssetDropTarget(point) {
  if (!visualFrameDocument) return null
  const frameWindow = visualPreviewFrame.value?.contentWindow
  if (!frameWindow?.document?.elementFromPoint) return null
  const frameRect = visualPreviewFrame.value?.getBoundingClientRect?.()
  if (!frameRect) return null
  const viewX = Number(point?.x || 0) - Number(frameWindow?.scrollX || 0)
  const viewY = Number(point?.y || 0) - Number(frameWindow?.scrollY || 0)
  if (viewX < 0 || viewY < 0 || viewX > frameRect.width || viewY > frameRect.height) return null
  let element = null
  try {
    element = frameWindow.document.elementFromPoint(viewX, viewY)
  } catch {
    element = null
  }
  if (!element) return null
  return element.closest?.('*') || element
}

function pickTokenTargetField(tokenName, targetElement = null) {
  const lower = String(tokenName || '').toLowerCase()
  const editableTarget = isVisualEditableElement(targetElement) ? targetElement : null
  const tag = String(editableTarget?.tagName || '').toLowerCase()
  if (lower.includes('font') || lower.includes('text')) return 'fontFamily'
  if (lower.includes('radius')) return 'borderRadius'
  if (lower.includes('shadow')) return 'boxShadow'
  if (lower.includes('color')) {
    if (tag === 'p' || tag === 'span' || tag === 'a' || tag === 'label' || tag === 'h1' || tag === 'h2' || tag === 'h3') return 'color'
    return 'backgroundColor'
  }
  return 'backgroundColor'
}

function applyAssetStyleEntriesToSelection(entries) {
  const rows = Array.isArray(entries) ? entries : []
  if (!rows.length) return false
  for (const row of rows) {
    const key = String(row?.key || '').trim()
    if (!key) continue
    applyVisualField(key, String(row?.value ?? ''))
  }
  return true
}

function applyImageSourceToSelection(value, options = {}) {
  const nextSource = normalizeImageAssetUrl(value)
  if (!nextSource) return false
  const selectedIds = Array.isArray(visualSelectedIds.value) && visualSelectedIds.value.length
    ? [...visualSelectedIds.value]
    : (visualSelectedId.value ? [visualSelectedId.value] : [])
  if (!selectedIds.length) return false

  pushVisualHistorySnapshot({ force: true })
  let structureChanged = false
  const backgroundNodeIds = []
  for (const nodeId of selectedIds) {
    const element = getVisualElementById(nodeId)
    if (!element || !isVisualEditableElement(element)) continue
    const tag = String(element.tagName || '').toLowerCase()
    if (tag === 'img') {
      if (String(element.getAttribute('src') || '').trim() !== nextSource) {
        element.setAttribute('src', nextSource)
        structureChanged = true
      }
      continue
    }
    if (tag === 'source') {
      if (String(element.getAttribute('srcset') || '').trim() !== nextSource) {
        element.setAttribute('srcset', nextSource)
        structureChanged = true
      }
      continue
    }
    if (tag === 'picture') {
      const imageNode = element.querySelector('img')
      if (imageNode) {
        if (String(imageNode.getAttribute('src') || '').trim() !== nextSource) {
          imageNode.setAttribute('src', nextSource)
          structureChanged = true
        }
      } else if (visualFrameDocument?.createElement) {
        const created = visualFrameDocument.createElement('img')
        created.setAttribute('src', nextSource)
        created.setAttribute('alt', fileNameFromUrl(nextSource))
        element.appendChild(created)
        structureChanged = true
      }
      for (const sourceNode of Array.from(element.querySelectorAll('source'))) {
        if (String(sourceNode.getAttribute('srcset') || '').trim() === nextSource) continue
        sourceNode.setAttribute('srcset', nextSource)
        structureChanged = true
      }
      continue
    }
    backgroundNodeIds.push(nodeId)
  }

  let styleChanged = false
  if (backgroundNodeIds.length) {
    const escaped = nextSource.replace(/"/g, '\\"')
    styleChanged = applyStyleBatchForNodes(backgroundNodeIds, [{ key: 'backgroundImage', value: `url("${escaped}")` }])
  }
  if (structureChanged) markVisualStructureDirty()
  if (visualSelectedElement) syncVisualPropsFromElement(visualSelectedElement)
  nextTick(() => {
    syncResizeOverlay()
    syncRedlineOverlay()
  })
  if (!options?.silentSuccess) {
    success.value = 'تصویر اعمال شد.'
    error.value = ''
  }
  return Boolean(styleChanged || structureChanged)
}

function createImageElementAtPoint(imageUrl, point, options = {}) {
  if (!visualFrameDocument?.body) return ''
  const src = normalizeImageAssetUrl(imageUrl)
  if (!src) return ''
  pushVisualHistorySnapshot({ force: true })
  const element = visualFrameDocument.createElement('img')
  element.setAttribute('src', src)
  element.setAttribute('alt', fileNameFromUrl(src))
  element.style.position = 'absolute'
  element.style.left = `${Math.round(Number(point?.x || 0))}px`
  element.style.top = `${Math.round(Number(point?.y || 0))}px`
  element.style.width = '240px'
  element.style.height = 'auto'
  element.style.objectFit = 'cover'
  element.style.zIndex = '10'
  visualFrameDocument.body.appendChild(element)
  const nodeId = upsertSingleLayerForElement(element)
  selectVisualLayer(nodeId)
  markVisualStructureDirty()
  if (!options?.silentSuccess) {
    success.value = 'تصویر به Canvas اضافه شد.'
    error.value = ''
  }
  return nodeId
}

async function insertAssetItem(asset, options = {}) {
  if (!asset || typeof asset !== 'object') return
  const type = String(asset.type || '').trim().toLowerCase()
  const point = options?.point && Number.isFinite(Number(options?.point?.x)) && Number.isFinite(Number(options?.point?.y))
    ? { x: Number(options.point.x), y: Number(options.point.y) }
    : null
  if (type === 'component' && asset.id && !asset.tool) {
    await createComponentInstance(asset.id, 'default', { point })
    return
  }
  if (asset.tool) {
    createElementByToolAtPoint(String(asset.tool || ''), point || { x: 120, y: 120 })
    setActiveTool('select')
    return
  }
  if (type === 'style') {
    if (point && visualFrameDocument) {
      const target = resolveAssetDropTarget(point)
      if (target && isVisualEditableElement(target)) {
        const id = ensureVisualNodeId(target)
        if (!visualLayerIndex.value[id]) upsertSingleLayerForElement(target)
        selectVisualLayer(id)
      }
    }
    applyAssetStyleEntriesToSelection(asset.styleEntries)
    success.value = 'Style asset اعمال شد.'
    return
  }
  if (type === 'token') {
    if (point && visualFrameDocument) {
      const target = resolveAssetDropTarget(point)
      if (target && isVisualEditableElement(target)) {
        const id = ensureVisualNodeId(target)
        if (!visualLayerIndex.value[id]) upsertSingleLayerForElement(target)
        selectVisualLayer(id)
      }
    }
    const tokenName = String(asset.tokenName || '').trim()
    if (!tokenName) return
    const tokenField = pickTokenTargetField(tokenName, visualSelectedElement)
    applyVisualField(tokenField, `var(${tokenName})`)
    success.value = 'Token روی المنت اعمال شد.'
    return
  }
  if (type === 'image') {
    if (point && visualFrameDocument) {
      const target = resolveAssetDropTarget(point)
      if (target && isVisualEditableElement(target)) {
        const id = ensureVisualNodeId(target)
        if (!visualLayerIndex.value[id]) upsertSingleLayerForElement(target)
        selectVisualLayer(id)
      }
    }
    const applied = applyImageAssetItem(asset, { point })
    if (!applied) error.value = 'اعمال تصویر انجام نشد.'
  }
}

async function onCanvasAssetDrop(payload) {
  const point = resolveCanvasDropPoint(payload)
  await insertAssetItem(payload?.asset, { point })
  draggingAssetItem.value = null
}

function onSourceCodeInput(value) {
  sourceCode.value = String(value || '')
}

function onRawCssInput(value) {
  rawCss.value = String(value || '')
}

function onNewElementFormUpdate(value) {
  if (!value || typeof value !== 'object') return
  newElementForm.value = { ...newElementForm.value, ...value }
}

function setPreviewFrameRef(el) {
  visualPreviewFrame.value = el || null
}

function setSourceCodeTextareaRef(el) {
  sourceCodeTextarea.value = el || null
}

function isColorFieldKey(fieldKey) {
  return ['color', 'backgroundColor', 'borderColor'].includes(String(fieldKey || '').trim())
}

function setActiveTool(toolKey) {
  activeTool.value = String(toolKey || 'select')
}

function normalizeViewportPreset(value) {
  const preset = String(value || '').trim().toLowerCase()
  if (preset === 'mobile') return 'mobile'
  if (preset === 'tablet') return 'tablet'
  return 'desktop'
}

function setViewportPreset(value) {
  viewportPreset.value = normalizeViewportPreset(value)
}

function clampCanvasZoom(value) {
  const numeric = Number(value || 1)
  if (!Number.isFinite(numeric)) return 1
  return Math.min(3, Math.max(0.25, Math.round(numeric * 100) / 100))
}

function setCanvasZoomHud(text) {
  canvasZoomHudText.value = String(text || `${Math.round(canvasZoom.value * 100)}%`)
  canvasZoomHudVisible.value = true
  if (canvasZoomHudTimer !== null) window.clearTimeout(canvasZoomHudTimer)
  canvasZoomHudTimer = window.setTimeout(() => {
    canvasZoomHudTimer = null
    canvasZoomHudVisible.value = false
  }, 900)
}

function applyCanvasZoomToDocument(doc) {
  if (!doc?.documentElement) return
  doc.documentElement.style.zoom = String(clampCanvasZoom(canvasZoom.value))
  syncResizeOverlay()
  syncCanvasDecorOverlays()
  syncRedlineOverlay()
}

function setCanvasZoom(value, options = {}) {
  const nextZoom = clampCanvasZoom(value)
  const previousZoom = clampCanvasZoom(canvasZoom.value)
  const frameWin = visualPreviewFrame.value?.contentWindow
  const doc = visualFrameDocument
  if (!doc?.documentElement || !frameWin) {
    canvasZoom.value = nextZoom
    if (!options?.silent) setCanvasZoomHud(`${Math.round(nextZoom * 100)}%`)
    return
  }

  const anchorX = Number.isFinite(Number(options?.anchorClientX))
    ? Number(options.anchorClientX)
    : Number(frameWin.innerWidth || 0) / 2
  const anchorY = Number.isFinite(Number(options?.anchorClientY))
    ? Number(options.anchorClientY)
    : Number(frameWin.innerHeight || 0) / 2
  const scrollX = Number(frameWin.scrollX || 0)
  const scrollY = Number(frameWin.scrollY || 0)
  const worldX = (anchorX + scrollX) / Math.max(0.01, previousZoom)
  const worldY = (anchorY + scrollY) / Math.max(0.01, previousZoom)

  canvasZoom.value = nextZoom
  doc.documentElement.style.zoom = String(nextZoom)

  const targetScrollX = Math.max(0, Math.round((worldX * nextZoom) - anchorX))
  const targetScrollY = Math.max(0, Math.round((worldY * nextZoom) - anchorY))
  try {
    frameWin.scrollTo({ left: targetScrollX, top: targetScrollY, behavior: 'auto' })
  } catch {
    frameWin.scrollTo(targetScrollX, targetScrollY)
  }
  syncResizeOverlay()
  syncCanvasDecorOverlays()
  syncRedlineOverlay()
  if (!options?.silent) setCanvasZoomHud(`${Math.round(nextZoom * 100)}%`)
}

function zoomCanvasByStep(direction = 1, options = {}) {
  const sign = Number(direction) >= 0 ? 1 : -1
  const factor = sign > 0 ? 1.1 : (1 / 1.1)
  setCanvasZoom(clampCanvasZoom(canvasZoom.value * factor), options)
}

function resetCanvasZoom() {
  setCanvasZoom(1)
}

function fitCanvasZoomToViewport() {
  const frameWin = visualPreviewFrame.value?.contentWindow
  const doc = visualFrameDocument
  if (!frameWin || !doc?.documentElement || !visualPreviewFrame.value) {
    setCanvasZoom(1)
    return
  }
  const docWidth = Math.max(
    Number(doc.documentElement?.scrollWidth || 0),
    Number(doc.body?.scrollWidth || 0),
    Number(frameWin.innerWidth || 0),
    1
  )
  const docHeight = Math.max(
    Number(doc.documentElement?.scrollHeight || 0),
    Number(doc.body?.scrollHeight || 0),
    Number(frameWin.innerHeight || 0),
    1
  )
  const frameRect = visualPreviewFrame.value.getBoundingClientRect?.()
  const availWidth = Math.max(120, Number(frameRect?.width || frameWin.innerWidth || 0) - 24)
  const availHeight = Math.max(120, Number(frameRect?.height || frameWin.innerHeight || 0) - 24)
  const fitZoom = clampCanvasZoom(Math.min(availWidth / docWidth, availHeight / docHeight))
  setCanvasZoom(fitZoom)
}

function readBooleanStorage(key, fallback = false) {
  try {
    const raw = window.localStorage.getItem(key)
    if (raw == null) return Boolean(fallback)
    return raw === '1' || raw === 'true'
  } catch {
    return Boolean(fallback)
  }
}

function readNumberStorage(key, fallback = 0, min = 1, max = 999) {
  try {
    const raw = window.localStorage.getItem(key)
    if (raw == null || raw === '') return Number(fallback || 0)
    const parsed = Number.parseInt(raw, 10)
    if (!Number.isFinite(parsed)) return Number(fallback || 0)
    return Math.min(Math.max(parsed, min), max)
  } catch {
    return Number(fallback || 0)
  }
}

function getLayerScanWorker() {
  if (typeof Worker === 'undefined') return null
  if (layerScanWorker) return layerScanWorker
  try {
    layerScanWorker = new LayerScannerWorker()
    return layerScanWorker
  } catch {
    layerScanWorker = null
    return null
  }
}

function terminateLayerScanWorker() {
  if (!layerScanWorker) return
  try { layerScanWorker.terminate() } catch { /* noop */ }
  layerScanWorker = null
}

function resolveElementByTreePath(doc, pathText) {
  if (!doc?.body) return null
  const path = String(pathText || '').trim()
  if (!path) return null
  const parts = path.split('.').map((row) => Number.parseInt(row, 10)).filter((row) => Number.isFinite(row) && row >= 0)
  if (!parts.length) return null
  let current = doc.body
  for (const index of parts) {
    const children = Array.from(current?.children || [])
    const next = children[index]
    if (!next) return null
    current = next
  }
  return current
}

function currentRecoverySessionKey() {
  const routeKey = String(route.value || '').trim()
  const fileKey = String(selectedTargetFile.value || '').trim()
  const branchKey = String(activeBranch.value || DEFAULT_EDITOR_BRANCH).trim() || DEFAULT_EDITOR_BRANCH
  return `${routeKey}::${fileKey}::${branchKey}`
}

function clearCrashRecoverySnapshot() {
  try {
    const raw = window.localStorage.getItem(CRASH_RECOVERY_STORAGE_KEY)
    if (!raw) return
    const parsed = JSON.parse(raw)
    const session = String(parsed?.session_key || '').trim()
    if (session !== currentRecoverySessionKey()) return
    window.localStorage.removeItem(CRASH_RECOVERY_STORAGE_KEY)
  } catch {
    // noop
  }
}

function persistCrashRecoverySnapshotNow() {
  if (!hasUnsavedChanges()) {
    clearCrashRecoverySnapshot()
    return
  }
  const payload = {
    session_key: currentRecoverySessionKey(),
    saved_at: new Date().toISOString(),
    route: String(route.value || ''),
    target_file: String(selectedTargetFile.value || ''),
    active_branch: String(activeBranch.value || DEFAULT_EDITOR_BRANCH),
    visual_overrides_map: visualOverridesMap.value || {},
    raw_css: String(rawCss.value || ''),
    source_code: String(sourceCode.value || ''),
    token_collections: cloneTokenCollections(tokenCollections.value),
    token_active_collection: String(activeTokenCollectionId.value || ''),
    token_active_mode: String(activeTokenMode.value || 'light'),
    prototype_model: normalizePrototypeModel(prototypeModel.value),
  }
  try {
    const serialized = JSON.stringify(payload)
    if (serialized.length > CRASH_RECOVERY_MAX_SERIALIZED) return
    window.localStorage.setItem(CRASH_RECOVERY_STORAGE_KEY, serialized)
  } catch {
    // noop
  }
}

function scheduleCrashRecoveryPersist() {
  if (crashRecoveryPersistTimer !== null) {
    window.clearTimeout(crashRecoveryPersistTimer)
  }
  crashRecoveryPersistTimer = window.setTimeout(() => {
    crashRecoveryPersistTimer = null
    persistCrashRecoverySnapshotNow()
  }, 900)
}

function maybeRestoreCrashRecoverySnapshot() {
  try {
    const raw = window.localStorage.getItem(CRASH_RECOVERY_STORAGE_KEY)
    if (!raw) return false
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object') return false
    const sessionKey = String(parsed.session_key || '').trim()
    if (!sessionKey || sessionKey !== currentRecoverySessionKey()) return false
    if (crashRecoveryPromptedSessionKey === sessionKey) return false
    crashRecoveryPromptedSessionKey = sessionKey
    const confirmed = window.confirm('یک draft ذخیره‌نشده از کرش/بستن قبلی پیدا شد. بازیابی شود؟')
    if (!confirmed) return false

    const recoveredMap = parsed.visual_overrides_map && typeof parsed.visual_overrides_map === 'object'
      ? parsed.visual_overrides_map
      : {}
    const normalizedMap = {}
    for (const row of Object.values(recoveredMap)) {
      const normalized = normalizeVisualOverrideItem(row)
      if (!normalized) continue
      normalizedMap[normalized.selector] = normalized
    }
    visualOverridesMap.value = normalizedMap
    rawCss.value = String(parsed.raw_css || '')
    sourceCode.value = String(parsed.source_code || sourceCode.value || '')
    const tokenSelection = resolveActiveTokenSelection(
      parsed.token_collections,
      String(parsed.token_active_collection || ''),
      String(parsed.token_active_mode || 'light')
    )
    tokenCollections.value = tokenSelection.collections
    activeTokenCollectionId.value = tokenSelection.collectionId
    activeTokenMode.value = tokenSelection.mode
    prototypeModel.value = normalizePrototypeModel(parsed.prototype_model)
    if (visualFrameDocument) {
      applyVisualOverridesToDocument(visualFrameDocument)
      applyRawCssToDocument(visualFrameDocument)
      applyActiveTokenModeToDocument(visualFrameDocument)
      applyPrototypeModelToDocument(visualFrameDocument)
      syncRedlineOverlay()
    }
    success.value = 'Draft بازیابی شد.'
    error.value = ''
    recomputeDirtyState()
    return true
  } catch {
    return false
  }
}

function normalizePrototypeFrameId(value) {
  let text = String(value || '').trim().toLowerCase()
  if (!text) return ''
  text = text.replace(/[^a-z0-9._-]/g, '-').replace(/-{2,}/g, '-').replace(/^[-._]+|[-._]+$/g, '')
  return text.slice(0, 80)
}

function normalizeBranchName(value) {
  let text = String(value || '').trim().toLowerCase()
  if (!text) return ''
  text = text.replace(/[^a-z0-9._/-]/g, '-').replace(/-{2,}/g, '-').replace(/^[-._/]+|[-._/]+$/g, '')
  return text.slice(0, 64)
}

function defaultPrototypeModel() {
  return {
    preview_enabled: false,
    start_frame_id: '',
    frames: {},
    links: [],
  }
}

function normalizePrototypeModel(input) {
  const source = input && typeof input === 'object' ? input : {}
  const rawFrames = source.frames && typeof source.frames === 'object' ? source.frames : {}
  const frames = {}
  for (const [rawId, rawRow] of Object.entries(rawFrames)) {
    const id = normalizePrototypeFrameId(rawId)
    const row = rawRow && typeof rawRow === 'object' ? rawRow : {}
    const selector = String(row.selector || '').trim()
    if (!id || !selector) continue
    frames[id] = {
      id,
      selector,
      label: String(row.label || id).trim().slice(0, 140),
    }
  }

  const rawLinks = Array.isArray(source.links) ? source.links : []
  const links = []
  const seen = new Set()
  for (const row of rawLinks) {
    const link = row && typeof row === 'object' ? row : {}
    const sourceId = normalizePrototypeFrameId(link.source_frame_id || link.source || '')
    const targetId = normalizePrototypeFrameId(link.target_frame_id || link.target || '')
    if (!sourceId || !targetId || !frames[sourceId] || !frames[targetId] || sourceId === targetId) continue
    const key = `${sourceId}->${targetId}`
    if (seen.has(key)) continue
    seen.add(key)
    const transition = (() => {
      const value = String(link.transition || 'instant').trim().toLowerCase()
      if (value === 'smart_animate') return 'smart-animate'
      return ['instant', 'dissolve', 'smart-animate'].includes(value) ? value : 'instant'
    })()
    links.push({
      id: String(link.id || key).trim().slice(0, 180),
      source_frame_id: sourceId,
      target_frame_id: targetId,
      trigger: 'click',
      transition,
      duration_ms: Math.min(8000, Math.max(60, Number.parseInt(String(link.duration_ms || '280'), 10) || 280)),
      smart_animate: Boolean(link.smart_animate || transition === 'smart-animate'),
    })
  }

  let startFrame = normalizePrototypeFrameId(source.start_frame_id || '')
  if (startFrame && !frames[startFrame]) startFrame = ''
  if (!startFrame && Object.keys(frames).length) startFrame = Object.keys(frames)[0]

  return {
    preview_enabled: Boolean(source.preview_enabled),
    start_frame_id: startFrame,
    frames,
    links,
  }
}

function normalizeComponentLibrary(input) {
  if (!input || typeof input !== 'object') return {}
  const output = {}
  for (const [rawId, rawItem] of Object.entries(input)) {
    const id = String(rawId || '').trim()
    if (!id || !rawItem || typeof rawItem !== 'object') continue
    const name = String(rawItem.name || id).trim() || id
    const variantsRaw = rawItem.variants && typeof rawItem.variants === 'object' ? rawItem.variants : {}
    const variants = {}
    for (const [variantKey, variantValue] of Object.entries(variantsRaw)) {
      const key = String(variantKey || '').trim() || 'default'
      const html = String(variantValue?.html || '').trim()
      if (!html) continue
      variants[key] = { html }
    }
    if (!variants.default && String(rawItem.master_html || '').trim()) {
      variants.default = { html: String(rawItem.master_html || '').trim() }
    }
    output[id] = {
      id,
      name,
      variants,
      master_html: String(rawItem.master_html || variants.default?.html || '').trim(),
      description: String(rawItem.description || '').trim(),
      version: Math.max(1, Number.parseInt(String(rawItem.version || '1'), 10) || 1),
      updated_at: String(rawItem.updated_at || '').trim(),
      published_at: String(rawItem.published_at || '').trim(),
    }
  }
  return output
}

function readComponentLibraryFromStorage() {
  try {
    const raw = window.localStorage.getItem(COMPONENT_LIBRARY_STORAGE_KEY)
    if (!raw) return {}
    const parsed = JSON.parse(raw)
    return normalizeComponentLibrary(parsed)
  } catch {
    return {}
  }
}

function persistComponentLibraryToStorage(nextLibrary) {
  try {
    const normalized = normalizeComponentLibrary(nextLibrary)
    window.localStorage.setItem(COMPONENT_LIBRARY_STORAGE_KEY, JSON.stringify(normalized))
  } catch {
    // noop
  }
}

function isTypingTarget(node) {
  const el = node && node.nodeType === Node.ELEMENT_NODE ? node : node?.parentElement
  if (!el) return false
  if (el.closest('input, textarea, select, [contenteditable="true"], [contenteditable=""]')) return true
  return false
}

function onCssVariableQueryInput(value) {
  cssVariableQuery.value = String(value || '')
}

function escapeRegex(value) {
  return String(value || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function upsertRootCssVariableInRawCss(cssText, variableName, variableValue) {
  const key = String(variableName || '').trim()
  if (!key.startsWith('--')) return String(cssText || '')
  const value = String(variableValue || '').trim()
  const source = String(cssText || '')
  const rootRegex = /:root\s*\{([\s\S]*?)\}/m
  const keyRegex = new RegExp(`(^|[;\\n\\r]\\s*)${escapeRegex(key)}\\s*:\\s*[^;]*;?`, 'm')

  if (rootRegex.test(source)) {
    const next = source.replace(rootRegex, (_match, bodyText) => {
      let body = String(bodyText || '')
      if (value) {
        if (keyRegex.test(body)) {
          body = body.replace(keyRegex, `$1${key}: ${value};`)
        } else {
          body = `${body.trim()}\n  ${key}: ${value};`
        }
      } else if (keyRegex.test(body)) {
        body = body.replace(keyRegex, '$1')
      }
      const compact = String(body || '').trim()
      return compact ? `:root {\n  ${compact.replace(/\n+/g, '\n  ')}\n}` : ':root {\n}'
    })
    return next
  }

  if (!value) return source
  const block = `:root {\n  ${key}: ${value};\n}`
  return source ? `${block}\n\n${source}` : block
}

function collectPreviewCssVariables(doc) {
  if (!doc || !doc.documentElement) return
  const rows = []
  try {
    const win = visualPreviewFrame.value?.contentWindow
    const computed = win?.getComputedStyle ? win.getComputedStyle(doc.documentElement) : null
    if (!computed) {
      cssVariables.value = []
      return
    }
    for (let idx = 0; idx < computed.length; idx += 1) {
      const name = String(computed[idx] || '').trim()
      if (!name.startsWith('--')) continue
      const value = String(computed.getPropertyValue(name) || '').trim()
      rows.push({ name, value })
    }
  } catch {
    // noop
  }
  cssVariables.value = rows.sort((a, b) => String(a.name || '').localeCompare(String(b.name || '')))
}

function onCssVariableUpdate(variableName, variableValue) {
  const key = String(variableName || '').trim()
  if (!key.startsWith('--')) return
  pushVisualHistorySnapshot({ force: true })
  const value = String(variableValue || '').trim()
  if (visualFrameDocument?.documentElement) {
    if (value) visualFrameDocument.documentElement.style.setProperty(key, value)
    else visualFrameDocument.documentElement.style.removeProperty(key)
  }
  rawCss.value = upsertRootCssVariableInRawCss(rawCss.value, key, value)
  collectPreviewCssVariables(visualFrameDocument)
}

function toKebabStyleKey(value) {
  const raw = String(value || '').trim()
  if (!raw) return ''
  if (raw.startsWith('--')) return raw
  return raw.replace(/([a-z0-9])([A-Z])/g, '$1-$2').replace(/[\s_]+/g, '-').toLowerCase()
}

function toStyleObjectKey(value) {
  const raw = String(value || '').trim()
  if (!raw) return ''
  if (raw.startsWith('--')) return raw
  if (!raw.includes('-')) return raw
  return raw.toLowerCase().replace(/-([a-z0-9])/g, (_, char) => char.toUpperCase())
}

const filteredStyleSections = computed(() => {
  const query = String(inspectorStyleQuery.value || '').trim().toLowerCase()
  if (!query) return styleSections
  const terms = new Set(query.split(/\s+/).filter(Boolean))
  const expandedTerms = new Set(terms)
  const aliasMap = {
    dimension: ['width', 'height', 'min-width', 'max-width', 'min-height', 'max-height', 'size'],
    dimensions: ['width', 'height', 'min-width', 'max-width', 'min-height', 'max-height', 'size'],
    size: ['width', 'height', 'min-width', 'max-width', 'min-height', 'max-height', 'dimension'],
    sizing: ['width', 'height', 'min-width', 'max-width', 'min-height', 'max-height'],
    position: ['top', 'right', 'bottom', 'left', 'z-index', 'rotation'],
    spacing: ['margin', 'padding', 'gap'],
  }
  for (const term of terms) {
    const aliases = aliasMap[term]
    if (!aliases) continue
    for (const alias of aliases) expandedTerms.add(String(alias || '').toLowerCase())
  }

  function matchesQuery(value) {
    const hay = String(value || '').toLowerCase()
    if (!hay) return false
    if (hay.includes(query)) return true
    for (const term of expandedTerms) {
      if (term && hay.includes(term)) return true
    }
    return false
  }

  const result = []
  for (const section of styleSections) {
    const sectionTitle = String(section?.title || '')
    const sectionMatches = matchesQuery(sectionTitle)
    const matchedFields = (section.fields || []).filter((field) => {
      const key = String(field?.key || '')
      const label = String(field?.label || '')
      const kebabKey = toKebabStyleKey(key)
      return matchesQuery(key) || matchesQuery(label) || matchesQuery(kebabKey)
    })
    if (!sectionMatches && !matchedFields.length) continue
    result.push({ ...section, fields: sectionMatches ? [...(section.fields || [])] : matchedFields })
  }
  return result
})

const rawStylePropertyOptions = computed(() => {
  const base = new Set(
    Object.keys(styleFieldOptions || {}).map((styleKey) => toKebabStyleKey(styleKey)).filter(Boolean)
  )
  ;[
    'background-image', 'background-size', 'background-position', 'object-fit', 'object-position',
    'cursor', 'pointer-events', 'grid-template-columns', 'grid-template-rows', 'grid-column',
    'grid-row', 'align-self', 'justify-self', 'transform', 'transform-origin', 'filter',
    'backdrop-filter', 'white-space', 'word-break', 'text-overflow', 'visibility'
  ].forEach((item) => base.add(item))
  return Array.from(base).sort((a, b) => a.localeCompare(b))
})

const filteredRawStylePropertyOptions = computed(() => {
  const query = String(rawStylePropertyQuery.value || '').trim().toLowerCase()
  if (!query) return rawStylePropertyOptions.value
  return rawStylePropertyOptions.value.filter((propertyName) =>
    String(propertyName || '').toLowerCase().includes(query)
  )
})

const selectedLayerStyleEntries = computed(() => {
  if (!visualSelectedLayer.value) return []
  const selector = String(visualSelectedLayer.value.selector || '').trim()
  if (!selector) return []
  const row = visualOverridesMap.value?.[selector]
  const styles = row?.styles && typeof row.styles === 'object' ? row.styles : {}
  const query = String(rawStylePropertyQuery.value || '').trim().toLowerCase()
  return Object.entries(styles)
    .map(([key, value]) => ({
      key,
      label: toKebabStyleKey(key),
      value: String(value ?? ''),
    }))
    .filter((entry) =>
      !query ||
      entry.label.toLowerCase().includes(query) ||
      entry.value.toLowerCase().includes(query)
    )
    .sort((a, b) => a.label.localeCompare(b.label))
})

const filteredCssVariables = computed(() => {
  const query = String(cssVariableQuery.value || '').trim().toLowerCase()
  const rows = Array.isArray(cssVariables.value) ? cssVariables.value : []
  if (!query) return rows
  return rows.filter((row) => {
    const name = String(row?.name || '').toLowerCase()
    const value = String(row?.value || '').toLowerCase()
    return name.includes(query) || value.includes(query)
  })
})

const textStyleTokens = computed(() =>
  (Array.isArray(cssVariables.value) ? cssVariables.value : [])
    .filter((row) => {
      const name = String(row?.name || '').toLowerCase()
      return (
        name.includes('font') ||
        name.includes('text') ||
        name.includes('heading') ||
        name.includes('typography')
      )
    })
)

const colorStyleTokens = computed(() =>
  (Array.isArray(cssVariables.value) ? cssVariables.value : []).filter((row) =>
    String(row?.name || '').toLowerCase().includes('color')
  )
)

function defaultSharedTextStyles() {
  return {
    body: {
      id: 'body',
      name: 'Body',
      styles: { fontFamily: "'Vazirmatn', sans-serif", fontSize: '16px', fontWeight: '400', lineHeight: '1.7', letterSpacing: '0', textAlign: 'right' },
    },
    'heading-md': {
      id: 'heading-md',
      name: 'Heading M',
      styles: { fontFamily: "'Vazirmatn', sans-serif", fontSize: '28px', fontWeight: '700', lineHeight: '1.35', letterSpacing: '-0.2px', textAlign: 'right' },
    },
    caption: {
      id: 'caption',
      name: 'Caption',
      styles: { fontFamily: "'Vazirmatn', sans-serif", fontSize: '12px', fontWeight: '400', lineHeight: '1.4', letterSpacing: '0.2px', textAlign: 'right' },
    },
  }
}

function normalizeSharedTextStyles(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) return defaultSharedTextStyles()
  const output = {}
  for (const [rawId, rawRow] of Object.entries(input)) {
    const id = String(rawId || '').trim().toLowerCase().replace(/[^a-z0-9_-]/g, '-')
    if (!id || !rawRow || typeof rawRow !== 'object') continue
    const name = String(rawRow.name || id).trim().slice(0, 120) || id
    const rawStyles = rawRow.styles && typeof rawRow.styles === 'object' ? rawRow.styles : {}
    const styles = {}
    for (const [rawKey, rawValue] of Object.entries(rawStyles)) {
      const key = String(rawKey || '').trim()
      const value = String(rawValue || '').trim()
      if (!key || !value) continue
      styles[key] = value.slice(0, 200)
    }
    if (!Object.keys(styles).length) continue
    output[id] = { id, name, styles }
  }
  if (!Object.keys(output).length) return defaultSharedTextStyles()
  return output
}

function readSharedTextStylesFromStorage() {
  try {
    const raw = window.localStorage.getItem(SHARED_TEXT_STYLE_STORAGE_KEY)
    if (!raw) return defaultSharedTextStyles()
    return normalizeSharedTextStyles(JSON.parse(raw))
  } catch {
    return defaultSharedTextStyles()
  }
}

function persistSharedTextStylesToStorage(nextStyles) {
  try {
    const normalized = normalizeSharedTextStyles(nextStyles)
    window.localStorage.setItem(SHARED_TEXT_STYLE_STORAGE_KEY, JSON.stringify(normalized))
  } catch {
    // noop
  }
}

const sharedTextStyleItems = computed(() =>
  Object.values(sharedTextStyles.value || {})
    .map((row) => ({ id: String(row.id || ''), name: String(row.name || row.id || '') }))
    .filter((row) => row.id)
    .sort((a, b) => a.name.localeCompare(b.name))
)

const selectedSharedTextStyleId = computed(() => {
  if (!visualSelectedElement) return ''
  const styleId = String(visualSelectedElement.getAttribute(TEXT_STYLE_LINK_ATTR) || '').trim()
  return styleId && sharedTextStyles.value?.[styleId] ? styleId : ''
})

function resolveVisualFieldValueForElement(element, fieldKey) {
  if (!element || element.nodeType !== 1) return ''
  const key = String(fieldKey || '').trim()
  if (!key) return ''
  if (key === 'text_content') return String(_quickTextOf(element) || '').trim()
  if (key === 'rotation') {
    const inlineTransform = String(element.style?.transform || '').trim()
    if (inlineTransform) {
      const parsed = splitTransformRotation(inlineTransform)
      return `${parsed.rotateDeg}deg`
    }
    try {
      const computed = visualPreviewFrame.value?.contentWindow?.getComputedStyle?.(element)
      const parsed = splitTransformRotation(String(computed?.transform || '').trim())
      return `${parsed.rotateDeg}deg`
    } catch {
      return ''
    }
  }
  if (key === 'paragraphSpacing') {
    const inlineValue = String(element.style.getPropertyValue('--mysite-paragraph-spacing') || '').trim()
    if (inlineValue) return inlineValue
    try {
      const computed = visualPreviewFrame.value?.contentWindow?.getComputedStyle?.(element)
      return String(computed?.getPropertyValue?.('--mysite-paragraph-spacing') || '').trim()
    } catch {
      return ''
    }
  }
  const inlineValue = String(element.style?.[key] || '').trim()
  if (inlineValue) return inlineValue
  try {
    const computed = visualPreviewFrame.value?.contentWindow?.getComputedStyle?.(element)
    return String(computed?.[key] || '').trim()
  } catch {
    return ''
  }
}

const mixedFieldKeys = computed(() => {
  const ids = getSelectedNodeIds()
  if (ids.length < 2) return {}
  const keys = Object.keys(visualProps.value || {})
  const output = {}
  for (const fieldKey of keys) {
    const values = new Set()
    for (const nodeId of ids) {
      const element = getVisualElementById(nodeId)
      values.add(resolveVisualFieldValueForElement(element, fieldKey))
      if (values.size > 1) break
    }
    if (values.size > 1) output[fieldKey] = true
  }
  return output
})

function getFieldOptions(fieldKey) {
  return Array.isArray(styleFieldOptions[fieldKey]) ? styleFieldOptions[fieldKey] : []
}

function getFieldSelectValue(fieldKey) {
  if (mixedFieldKeys.value?.[fieldKey]) return '__mixed__'
  const value = String(visualProps.value?.[fieldKey] ?? '').trim()
  if (!value) return ''
  const options = getFieldOptions(fieldKey)
  if (!options.length) return ''
  if (options.includes(value)) return value
  return '__custom__'
}

function shouldShowCustomInput(fieldKey) {
  if (mixedFieldKeys.value?.[fieldKey]) return false
  const options = getFieldOptions(fieldKey)
  if (!options.length) return true
  return Boolean(customFieldMode.value?.[fieldKey]) || getFieldSelectValue(fieldKey) === '__custom__'
}

const selectedOverriddenFieldSet = computed(() => {
  const output = new Set()
  const selectedIds = getSelectedNodeIds()
  if (!selectedIds.length) return output
  for (const nodeId of selectedIds) {
    const layer = visualLayerIndex.value?.[nodeId]
    const element = getVisualElementById(nodeId)
    if (!layer || !element) continue
    const selector = String(layer.selector || '').trim() || ensureLayerSelector(nodeId, element)
    if (!selector) continue
    const row = visualOverridesMap.value?.[selector]
    if (!row || typeof row !== 'object') continue
    const styles = row.styles && typeof row.styles === 'object' ? row.styles : {}
    for (const key of Object.keys(styles)) {
      const styleKey = String(key || '').trim()
      if (styleKey) output.add(styleKey)
    }
  }
  return output
})

function isVisualFieldOverridden(fieldKey) {
  let styleKey = String(fieldKey || '').trim()
  if (styleKey === 'rotation') styleKey = 'transform'
  if (!styleKey) return false
  return selectedOverriddenFieldSet.value.has(styleKey)
}

function onFieldPresetChange(fieldKey, value) {
  const nextValue = String(value ?? '')
  if (nextValue === '__mixed__') return
  if (nextValue === '__custom__') {
    customFieldMode.value = { ...customFieldMode.value, [fieldKey]: true }
    return
  }
  customFieldMode.value = { ...customFieldMode.value, [fieldKey]: false }
  applyVisualField(fieldKey, nextValue)
}

function onFieldInputChange(fieldKey, value) {
  customFieldMode.value = { ...customFieldMode.value, [fieldKey]: true }
  applyVisualField(fieldKey, value)
}

function onFieldRevert(fieldKey) {
  const key = String(fieldKey || '').trim()
  if (!key) return
  customFieldMode.value = { ...customFieldMode.value, [key]: false }
  applyVisualField(key === 'rotation' ? 'rotation' : key, '')
  nextTick(() => {
    if (!visualSelectedElement) return
    syncVisualPropsFromElement(visualSelectedElement)
  })
}

function isStyleSectionExpanded(sectionKey) {
  const key = String(sectionKey || '').trim()
  if (!key) return true
  return styleSectionOpen.value?.[key] !== false
}

function toggleStyleSection(sectionKey) {
  const key = String(sectionKey || '').trim()
  if (!key) return
  styleSectionOpen.value = { ...styleSectionOpen.value, [key]: !isStyleSectionExpanded(key) }
}

function escapeAttributeValue(value) {
  return String(value ?? '').replace(/&/g, '&amp;').replace(/"/g, '&quot;')
}

function escapeHtmlText(value) {
  return String(value ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function resolveBuilderTag() {
  const raw = newElementForm.value.tag === 'custom' ? newElementForm.value.customTag : newElementForm.value.tag
  const tag = String(raw || '').trim().toLowerCase()
  if (!/^[a-z][a-z0-9-]*$/.test(tag)) return ''
  return tag
}

function buildElementBlueprint() {
  const tag = resolveBuilderTag()
  if (!tag) throw new Error('Tag معتبر نیست.')
  const attrs = {}
  if (newElementForm.value.id) attrs.id = String(newElementForm.value.id || '').trim()
  if (newElementForm.value.className) attrs.class = String(newElementForm.value.className || '').trim()
  if (tag === 'a' && newElementForm.value.href) attrs.href = String(newElementForm.value.href || '').trim()
  if (tag === 'img' && newElementForm.value.src) attrs.src = String(newElementForm.value.src || '').trim()
  if (tag === 'img' && newElementForm.value.alt) attrs.alt = String(newElementForm.value.alt || '').trim()
  const text = String(newElementForm.value.text || '')
  const selfClosing = SELF_CLOSING_TAGS.has(tag)
  return { tag, attrs, text, selfClosing }
}

function buildElementSnippet() {
  const blueprint = buildElementBlueprint()
  const attrs = Object.entries(blueprint.attrs || {}).filter(([k, v]) => k && String(v || '').trim()).map(([k, v]) => `${k}="${escapeAttributeValue(v)}"`)
  const attrText = attrs.length ? ` ${attrs.join(' ')}` : ''
  if (blueprint.selfClosing) return `<${blueprint.tag}${attrText} />`
  return `<${blueprint.tag}${attrText}>${escapeHtmlText(blueprint.text || '')}</${blueprint.tag}>`
}

function buildPreviewElement(doc, blueprint) {
  const element = doc.createElement(blueprint.tag)
  for (const [key, value] of Object.entries(blueprint.attrs || {})) {
    const raw = String(value || '').trim()
    if (!raw) continue
    element.setAttribute(key, raw)
  }
  if (!blueprint.selfClosing && String(blueprint.text || '').trim()) element.textContent = String(blueprint.text || '')
  return element
}

async function insertElementSnippet() {
  try {
    const snippet = buildElementSnippet()
    const textarea = sourceCodeTextarea.value
    if (textarea && typeof textarea.selectionStart === 'number') {
      const start = Number(textarea.selectionStart || 0)
      const end = Number(textarea.selectionEnd || start)
      sourceCode.value = `${sourceCode.value.slice(0, start)}${snippet}${sourceCode.value.slice(end)}`
      await nextTick()
      const cursor = start + snippet.length
      textarea.focus()
      textarea.setSelectionRange(cursor, cursor)
    } else {
      sourceCode.value = `${String(sourceCode.value || '')}\n${snippet}`.trim()
    }
    success.value = 'اسنیپت اضافه شد.'
    error.value = ''
  } catch (err) {
    error.value = err?.message || 'افزودن المنت انجام نشد.'
    success.value = ''
  }
}

function addElementToPreview() {
  try {
    if (!visualFrameDocument || !visualFrameDocument.body) throw new Error('ابتدا پیش‌نمایش را بارگذاری کن.')
    pushVisualHistorySnapshot({ force: true })
    const blueprint = buildElementBlueprint()
    const parent = visualSelectedElement && isVisualEditableElement(visualSelectedElement) ? visualSelectedElement : visualFrameDocument.body
    const element = buildPreviewElement(visualFrameDocument, blueprint)
    parent.appendChild(element)
    const nodeId = upsertSingleLayerForElement(element)
    selectVisualLayer(nodeId)
    markVisualStructureDirty()
    success.value = 'المنت به پیش‌نمایش اضافه شد.'
    error.value = ''
  } catch (err) {
    error.value = err?.message || 'افزودن المنت در پیش‌نمایش انجام نشد.'
    success.value = ''
  }
}

function resolveCenterPointInPreview() {
  const frameRect = visualPreviewFrame.value?.getBoundingClientRect?.()
  const frameWindow = visualPreviewFrame.value?.contentWindow
  if (!frameRect || !frameWindow) return { x: 140, y: 120 }
  return {
    x: Math.max(0, Math.round((frameRect.width / 2) + Number(frameWindow.scrollX || 0) - 140)),
    y: Math.max(0, Math.round((frameRect.height / 2) + Number(frameWindow.scrollY || 0) - 90)),
  }
}

function createFramePresetFromToolbar(presetKey) {
  const key = String(presetKey || 'desktop').trim().toLowerCase()
  const preset = FRAME_PRESET_CONFIG[key] || FRAME_PRESET_CONFIG.desktop
  const point = resolveCenterPointInPreview()
  const nodeId = createElementByToolAtPoint('frame', point)
  if (!nodeId) return
  const element = getVisualElementById(nodeId)
  if (!element) return
  element.setAttribute(LAYER_LABEL_ATTR, String(preset.label || 'Frame'))
  applyStyleBatchForNodes([nodeId], [
    { key: 'width', value: `${Math.max(120, Number(preset.width || 320))}px` },
    { key: 'height', value: `${Math.max(120, Number(preset.height || 240))}px` },
    { key: 'borderStyle', value: 'solid' },
    { key: 'borderColor', value: 'rgba(13, 153, 255, 0.85)' },
    { key: 'borderWidth', value: '1px' },
    { key: 'backgroundColor', value: 'rgba(13, 153, 255, 0.05)' },
  ])
  syncLayerMetaFromElement(nodeId, element)
  success.value = `${preset.label} اضافه شد.`
  error.value = ''
}

async function applyBooleanOperation(operation) {
  if (!visualFrameDocument) return false
  const op = String(operation || '').trim().toLowerCase()
  if (!['union', 'subtract', 'intersect', 'exclude'].includes(op)) return false
  const elements = getSelectedElementsInDomOrder()
  if (elements.length < 2) return false
  const parent = elements[0]?.parentElement
  if (!parent || !elements.every((row) => row.parentElement === parent)) {
    error.value = 'برای Boolean ops، همه لایه‌ها باید هم‌سطح باشند.'
    return false
  }

  pushVisualHistorySnapshot({ force: true })
  const wrapper = visualFrameDocument.createElement('div')
  wrapper.className = 'mysite-ve-boolean'
  wrapper.setAttribute('data-mysite-boolean-op', op)
  wrapper.setAttribute(LAYER_LABEL_ATTR, `Boolean ${op}`)
  wrapper.style.position = 'relative'
  wrapper.style.display = 'block'
  wrapper.style.minHeight = '20px'
  wrapper.style.mixBlendMode = op === 'subtract' ? 'difference' : op === 'intersect' ? 'multiply' : op === 'exclude' ? 'exclusion' : 'normal'
  parent.insertBefore(wrapper, elements[0])
  for (const element of elements) wrapper.appendChild(element)
  const wrapperId = upsertSingleLayerForElement(wrapper)
  await runVisualLayerScan(visualFrameDocument, { loadToken: previewFrameLoadToken, focusNodeId: wrapperId })
  selectVisualLayer(wrapperId)
  markVisualStructureDirty()
  success.value = `Boolean (${op}) اعمال شد.`
  error.value = ''
  return true
}

async function flattenSelectedElements() {
  if (!visualFrameDocument) return false
  const elements = getSelectedElementsInDomOrder()
  if (!elements.length) return false
  const parent = elements[0]?.parentElement
  if (!parent || !elements.every((row) => row.parentElement === parent)) {
    error.value = 'برای Flatten، همه لایه‌ها باید هم‌سطح باشند.'
    return false
  }

  pushVisualHistorySnapshot({ force: true })
  const rects = elements.map((row) => row.getBoundingClientRect())
  const minLeft = Math.min(...rects.map((row) => row.left))
  const minTop = Math.min(...rects.map((row) => row.top))
  const maxRight = Math.max(...rects.map((row) => row.right))
  const maxBottom = Math.max(...rects.map((row) => row.bottom))
  const parentRect = parent.getBoundingClientRect()
  const basis = elements[0]

  const flattened = visualFrameDocument.createElement('div')
  flattened.className = 'mysite-ve-flattened'
  flattened.setAttribute('data-mysite-flatten', '1')
  flattened.setAttribute(LAYER_LABEL_ATTR, 'Flattened Shape')
  flattened.style.position = 'absolute'
  flattened.style.left = `${Math.max(0, Math.round(minLeft - parentRect.left))}px`
  flattened.style.top = `${Math.max(0, Math.round(minTop - parentRect.top))}px`
  flattened.style.width = `${Math.max(20, Math.round(maxRight - minLeft))}px`
  flattened.style.height = `${Math.max(20, Math.round(maxBottom - minTop))}px`
  flattened.style.borderRadius = String(basis.style.borderRadius || '10px')
  flattened.style.background = String(basis.style.background || basis.style.backgroundColor || 'rgba(13, 153, 255, 0.2)')
  flattened.style.border = String(basis.style.border || '1px solid rgba(13, 153, 255, 0.8)')
  flattened.style.boxShadow = String(basis.style.boxShadow || 'none')

  parent.insertBefore(flattened, elements[0])
  for (const element of elements) element.remove()
  const nodeId = upsertSingleLayerForElement(flattened)
  await runVisualLayerScan(visualFrameDocument, { loadToken: previewFrameLoadToken, focusNodeId: nodeId })
  selectVisualLayer(nodeId)
  markVisualStructureDirty()
  success.value = 'Flatten انجام شد.'
  error.value = ''
  return true
}

async function maskSelectedElements() {
  if (!visualFrameDocument) return false
  const elements = getSelectedElementsInDomOrder()
  if (elements.length < 2) return false
  const parent = elements[0]?.parentElement
  if (!parent || !elements.every((row) => row.parentElement === parent)) {
    error.value = 'برای Mask، همه لایه‌ها باید هم‌سطح باشند.'
    return false
  }

  const selectedPrimary = getVisualElementById(visualSelectedId.value)
  const maskElement = selectedPrimary && elements.includes(selectedPrimary) ? selectedPrimary : elements[0]
  const contentElements = elements.filter((row) => row !== maskElement)
  if (!maskElement || !contentElements.length) return false

  pushVisualHistorySnapshot({ force: true })
  const maskRect = maskElement.getBoundingClientRect()
  const parentRect = parent.getBoundingClientRect()
  const wrapper = visualFrameDocument.createElement('div')
  wrapper.className = 'mysite-ve-mask'
  wrapper.setAttribute('data-mysite-mask', '1')
  wrapper.setAttribute(LAYER_LABEL_ATTR, 'Mask Group')
  wrapper.style.position = 'absolute'
  wrapper.style.left = `${Math.max(0, Math.round(maskRect.left - parentRect.left))}px`
  wrapper.style.top = `${Math.max(0, Math.round(maskRect.top - parentRect.top))}px`
  wrapper.style.width = `${Math.max(10, Math.round(maskRect.width))}px`
  wrapper.style.height = `${Math.max(10, Math.round(maskRect.height))}px`
  wrapper.style.overflow = 'hidden'
  wrapper.style.borderRadius = String(maskElement.style.borderRadius || '0')

  parent.insertBefore(wrapper, elements[0])

  for (const row of contentElements) {
    const rect = row.getBoundingClientRect()
    row.style.position = 'absolute'
    row.style.left = `${Math.round(rect.left - maskRect.left)}px`
    row.style.top = `${Math.round(rect.top - maskRect.top)}px`
    wrapper.appendChild(row)
  }
  maskElement.remove()

  const wrapperId = upsertSingleLayerForElement(wrapper)
  await runVisualLayerScan(visualFrameDocument, { loadToken: previewFrameLoadToken, focusNodeId: wrapperId })
  selectVisualLayer(wrapperId)
  markVisualStructureDirty()
  success.value = 'Mask group ساخته شد.'
  error.value = ''
  return true
}

function sanitizeClonedElementTree(rootElement, doc) {
  const stack = [rootElement]
  while (stack.length) {
    const node = stack.pop()
    if (!node || node.nodeType !== 1) continue
    node.classList?.remove('mysite-visual-selected')
    node.removeAttribute(VISUAL_NODE_ATTR)
    const currentId = String(node.id || '').trim()
    if (currentId) {
      const baseId = `${currentId}-copy`
      let candidate = baseId
      let idx = 1
      while (doc.getElementById(candidate)) {
        candidate = `${baseId}-${idx}`
        idx += 1
      }
      node.id = candidate
    }
    for (const child of Array.from(node.children || [])) stack.push(child)
  }
}

function duplicateSelectedElement() {
  try {
    if (!visualFrameDocument) throw new Error('ابتدا یک المنت انتخاب کن.')
    const selectedElements = getSelectedElementsInDomOrder()
    if (!selectedElements.length) throw new Error('ابتدا یک المنت انتخاب کن.')
    pushVisualHistorySnapshot({ force: true })
    const duplicatedIds = []
    for (const element of selectedElements) {
      const parent = element.parentElement
      if (!parent) continue
      const clone = element.cloneNode(true)
      sanitizeClonedElementTree(clone, visualFrameDocument)
      parent.insertBefore(clone, element.nextSibling)
      const nodeId = upsertSingleLayerForElement(clone)
      if (nodeId) duplicatedIds.push(nodeId)
    }
    if (!duplicatedIds.length) throw new Error('Duplicate انجام نشد.')
    const primaryId = duplicatedIds[duplicatedIds.length - 1]
    selectVisualLayer(primaryId)
    for (const extraId of duplicatedIds.slice(0, -1)) {
      selectVisualLayer(extraId, { additive: true, toggle: false })
    }
    markVisualStructureDirty()
    success.value = 'المنت duplicate شد.'
    error.value = ''
  } catch (err) {
    error.value = err?.message || 'Duplicate انجام نشد.'
    success.value = ''
  }
}

async function deleteSelectedElement() {
  if (!visualFrameDocument) return false
  const selectedElements = getSelectedElementsInDomOrder()
  if (!selectedElements.length) return false
  pushVisualHistorySnapshot({ force: true })
  const map = { ...visualOverridesMap.value }
  for (const element of selectedElements) {
    if (!element.parentElement) continue
    const nodeId = String(element.getAttribute(VISUAL_NODE_ATTR) || '').trim()
    const selector = nodeId ? ensureLayerSelector(nodeId, element) : ''
    if (selector && map[selector]) delete map[selector]
    element.remove()
  }
  visualOverridesMap.value = map
  clearVisualSelection()

  await runVisualLayerScan(visualFrameDocument, { loadToken: previewFrameLoadToken })
  markVisualStructureDirty()
  success.value = 'کامپوننت حذف شد.'
  error.value = ''
  return true
}

function nudgeSelectedElement(dx, dy) {
  const selectedIds = Array.isArray(visualSelectedIds.value) && visualSelectedIds.value.length
    ? [...visualSelectedIds.value]
    : (visualSelectedId.value ? [visualSelectedId.value] : [])
  if (!selectedIds.length) return false
  pushVisualHistorySnapshot()
  const map = { ...visualOverridesMap.value }
  for (const nodeId of selectedIds) {
    const target = getVisualElementById(nodeId)
    const layer = visualLayerIndex.value?.[nodeId]
    if (!target || !layer) continue
    let positionValue = String(target.style.position || '').trim()
    if (!positionValue || positionValue === 'static') {
      positionValue = 'relative'
      target.style.position = 'relative'
    }
    const currentLeft = Number.parseFloat(target.style.left || '0') || 0
    const currentTop = Number.parseFloat(target.style.top || '0') || 0
    const nextLeft = Math.round(currentLeft + Number(dx || 0))
    const nextTop = Math.round(currentTop + Number(dy || 0))
    target.style.left = `${nextLeft}px`
    target.style.top = `${nextTop}px`
    const selector = ensureLayerSelector(nodeId, target)
    if (!selector) continue
    const existing = map[selector]
      ? { ...map[selector], styles: { ...(map[selector].styles || {}) } }
      : { selector, tag: layer.tag, label: layer.label, styles: {}, apply_text: false, text_content: '', apply_html: false, html_content: '' }
    existing.styles.position = positionValue || 'relative'
    existing.styles.left = `${nextLeft}px`
    existing.styles.top = `${nextTop}px`
    map[selector] = existing
    if (nodeId === visualSelectedId.value) {
      visualProps.value.position = existing.styles.position
      visualProps.value.left = existing.styles.left
      visualProps.value.top = existing.styles.top
    }
  }
  visualOverridesMap.value = map
  nextTick(() => { syncResizeOverlay(); syncRedlineOverlay() })
  return true
}

async function copySelectedElementToClipboard() {
  const selectedElements = getSelectedElementsInDomOrder()
  if (!selectedElements.length) return false
  const rows = []
  for (const element of selectedElements) {
    const clone = element.cloneNode(true)
    if (clone && clone.nodeType === 1) sanitizeClonedElementTree(clone, visualFrameDocument)
    if (clone?.outerHTML) rows.push(String(clone.outerHTML))
  }
  visualClipboardHtml = rows.join('\n')
  if (!visualClipboardHtml) return false
  try {
    if (navigator?.clipboard?.writeText) await navigator.clipboard.writeText(visualClipboardHtml)
  } catch {
    // ignore clipboard permission errors and keep internal clipboard
  }
  success.value = 'کامپوننت کپی شد.'
  error.value = ''
  return true
}

async function pasteClipboardElement() {
  if (!visualFrameDocument?.body) return false
  let markup = String(visualClipboardHtml || '').trim()
  if (!markup) {
    try {
      if (navigator?.clipboard?.readText) markup = String((await navigator.clipboard.readText()) || '').trim()
    } catch {
      markup = ''
    }
  }
  if (!markup) return false

  pushVisualHistorySnapshot({ force: true })
  const parent = visualSelectedElement?.parentElement || visualFrameDocument.body
  const anchor = visualSelectedElement?.nextSibling || null
  const parser = visualFrameDocument.createElement('template')
  parser.innerHTML = markup
  const rows = Array.from(parser.content?.children || []).filter((row) => isVisualEditableElement(row))
  if (!rows.length) return false
  const pastedIds = []
  for (const element of rows) {
    sanitizeClonedElementTree(element, visualFrameDocument)
    parent.insertBefore(element, anchor)
    const nodeId = upsertSingleLayerForElement(element)
    if (nodeId) pastedIds.push(nodeId)
  }
  if (!pastedIds.length) return false
  const primaryId = pastedIds[pastedIds.length - 1]
  selectVisualLayer(primaryId)
  for (const extraId of pastedIds.slice(0, -1)) {
    selectVisualLayer(extraId, { additive: true, toggle: false })
  }
  markVisualStructureDirty()
  success.value = 'کامپوننت Paste شد.'
  error.value = ''
  return true
}

function applyStyleBatchForNodes(nodeIds, styleEntries) {
  const ids = Array.isArray(nodeIds) ? nodeIds.map((row) => String(row || '').trim()).filter(Boolean) : []
  if (!ids.length || !Array.isArray(styleEntries) || !styleEntries.length) return false
  const map = { ...visualOverridesMap.value }
  for (const nodeId of ids) {
    const element = getVisualElementById(nodeId)
    const layer = visualLayerIndex.value?.[nodeId]
    if (!element || !layer) continue
    if (isLayerLockedElement(element)) continue
    const selector = ensureLayerSelector(nodeId, element)
    if (!selector) continue
    const row = map[selector]
      ? { ...map[selector], styles: { ...(map[selector].styles || {}) } }
      : { selector, tag: layer.tag, label: layer.label, styles: {}, apply_text: false, text_content: '', apply_html: false, html_content: '' }
    for (const entry of styleEntries) {
      const styleKey = String(entry?.key || '').trim()
      if (!styleKey) continue
      const styleValue = String(entry?.value ?? '').trim()
      if (styleValue) {
        row.styles[styleKey] = styleValue
        if (styleKey.startsWith('--') || styleKey.includes('-')) element.style.setProperty(styleKey, styleValue)
        else element.style[styleKey] = styleValue
      } else {
        delete row.styles[styleKey]
        if (styleKey.startsWith('--') || styleKey.includes('-')) element.style.removeProperty(styleKey)
        else element.style[styleKey] = ''
      }
      if (nodeId === visualSelectedId.value) visualProps.value[styleKey] = styleValue
    }
    if (!row.apply_text && !row.apply_html && !Object.keys(row.styles || {}).length) delete map[selector]
    else map[selector] = row
  }
  visualOverridesMap.value = map
  return true
}

function alignAndDistributeSelection(action) {
  const selectedIds = Array.isArray(visualSelectedIds.value) && visualSelectedIds.value.length
    ? [...visualSelectedIds.value]
    : (visualSelectedId.value ? [visualSelectedId.value] : [])
  if (selectedIds.length < 2) return false
  const actionKey = String(action || '').trim()
  if (!actionKey) return false

  const records = selectedIds
    .map((nodeId) => {
      const element = getVisualElementById(nodeId)
      if (!element) return null
      return { nodeId, element, rect: element.getBoundingClientRect() }
    })
    .filter(Boolean)
  if (records.length < 2) return false

  pushVisualHistorySnapshot({ force: true })

  const makeUpdate = (record, nextLeft, nextTop) => {
    const element = record.element
    const currentLeft = Number.parseFloat(element.style.left || '0') || 0
    const currentTop = Number.parseFloat(element.style.top || '0') || 0
    const dx = Math.round(nextLeft - record.rect.left)
    const dy = Math.round(nextTop - record.rect.top)
    const finalLeft = currentLeft + dx
    const finalTop = currentTop + dy
    element.style.position = element.style.position || 'relative'
    element.style.left = `${finalLeft}px`
    element.style.top = `${finalTop}px`
    return { nodeId: record.nodeId, left: `${finalLeft}px`, top: `${finalTop}px`, position: 'relative' }
  }

  const leftEdge = Math.min(...records.map((row) => row.rect.left))
  const rightEdge = Math.max(...records.map((row) => row.rect.right))
  const topEdge = Math.min(...records.map((row) => row.rect.top))
  const bottomEdge = Math.max(...records.map((row) => row.rect.bottom))
  const centerX = (leftEdge + rightEdge) / 2
  const centerY = (topEdge + bottomEdge) / 2
  const updates = []

  if (actionKey === 'align-left') {
    for (const row of records) updates.push(makeUpdate(row, leftEdge, row.rect.top))
  } else if (actionKey === 'align-center') {
    for (const row of records) updates.push(makeUpdate(row, centerX - (row.rect.width / 2), row.rect.top))
  } else if (actionKey === 'align-right') {
    for (const row of records) updates.push(makeUpdate(row, rightEdge - row.rect.width, row.rect.top))
  } else if (actionKey === 'align-top') {
    for (const row of records) updates.push(makeUpdate(row, row.rect.left, topEdge))
  } else if (actionKey === 'align-middle') {
    for (const row of records) updates.push(makeUpdate(row, row.rect.left, centerY - (row.rect.height / 2)))
  } else if (actionKey === 'align-bottom') {
    for (const row of records) updates.push(makeUpdate(row, row.rect.left, bottomEdge - row.rect.height))
  } else if (actionKey === 'dist-h') {
    const rows = [...records].sort((a, b) => a.rect.left - b.rect.left)
    const span = rows[rows.length - 1].rect.left - rows[0].rect.left
    const step = rows.length > 1 ? (span / (rows.length - 1)) : 0
    rows.forEach((row, index) => updates.push(makeUpdate(row, rows[0].rect.left + (index * step), row.rect.top)))
  } else if (actionKey === 'dist-v') {
    const rows = [...records].sort((a, b) => a.rect.top - b.rect.top)
    const span = rows[rows.length - 1].rect.top - rows[0].rect.top
    const step = rows.length > 1 ? (span / (rows.length - 1)) : 0
    rows.forEach((row, index) => updates.push(makeUpdate(row, row.rect.left, rows[0].rect.top + (index * step))))
  } else {
    return false
  }

  for (const update of updates) {
    applyStyleBatchForNodes([update.nodeId], [
      { key: 'position', value: update.position },
      { key: 'left', value: update.left },
      { key: 'top', value: update.top },
    ])
  }
  success.value = 'Align/Distribute اعمال شد.'
  error.value = ''
  nextTick(() => { syncResizeOverlay(); syncRedlineOverlay() })
  return true
}

async function groupSelectedElements() {
  if (!visualFrameDocument) return false
  const elements = getSelectedElementsInDomOrder()
  if (elements.length < 2) return false
  const parent = elements[0]?.parentElement
  if (!parent) return false
  if (!elements.every((row) => row.parentElement === parent)) {
    error.value = 'برای Group کردن، همه آیتم‌ها باید هم‌سطح باشند.'
    return false
  }
  pushVisualHistorySnapshot({ force: true })
  const wrapper = visualFrameDocument.createElement('div')
  wrapper.className = 'mysite-ve-group'
  wrapper.setAttribute('data-mysite-group', '1')
  wrapper.style.display = 'block'
  wrapper.style.minHeight = '20px'
  parent.insertBefore(wrapper, elements[0])
  for (const element of elements) wrapper.appendChild(element)
  const groupId = upsertSingleLayerForElement(wrapper)
  await runVisualLayerScan(visualFrameDocument, { loadToken: previewFrameLoadToken, focusNodeId: groupId })
  selectVisualLayer(groupId)
  markVisualStructureDirty()
  success.value = 'Group ساخته شد.'
  error.value = ''
  return true
}

async function ungroupSelectedElements() {
  if (!visualSelectedElement || !visualFrameDocument) return false
  const target = visualSelectedElement
  const isGroup = target.getAttribute('data-mysite-group') === '1' || target.classList.contains('mysite-ve-group')
  if (!isGroup) return false
  const parent = target.parentElement
  if (!parent) return false
  pushVisualHistorySnapshot({ force: true })
  const children = Array.from(target.children || []).filter((row) => isVisualEditableElement(row))
  let focusNodeId = ''
  for (const child of children) {
    parent.insertBefore(child, target)
    if (!focusNodeId) focusNodeId = ensureVisualNodeId(child)
  }
  target.remove()
  await runVisualLayerScan(visualFrameDocument, { loadToken: previewFrameLoadToken, focusNodeId })
  if (focusNodeId) selectVisualLayer(focusNodeId)
  markVisualStructureDirty()
  success.value = 'Group باز شد.'
  error.value = ''
  return true
}

function buildComponentId(seed = 'component') {
  const base = String(seed || 'component').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'component'
  return `${base}-${Math.random().toString(36).slice(2, 8)}`
}

const COMPONENT_PRESERVED_STYLE_KEYS = [
  'position', 'left', 'top', 'right', 'bottom',
  'width', 'height', 'minWidth', 'minHeight', 'maxWidth', 'maxHeight',
  'transform', 'zIndex', 'display', 'margin', 'padding',
]

function collectPreservedComponentStyles(element, rowStyles = {}) {
  const out = {}
  for (const key of COMPONENT_PRESERVED_STYLE_KEYS) {
    const styleValue = String(rowStyles?.[key] || element?.style?.[key] || '').trim()
    if (!styleValue) continue
    out[key] = styleValue
  }
  return out
}

function stampComponentRecord(record, options = {}) {
  const now = new Date().toISOString()
  const currentVersion = Math.max(1, Number.parseInt(String(record?.version || '1'), 10) || 1)
  const nextVersion = options.bumpVersion ? currentVersion + 1 : currentVersion
  return {
    ...record,
    version: nextVersion,
    updated_at: now,
    published_at: options.publish ? now : String(record?.published_at || ''),
  }
}

function ensureComponentVariantMarkup(record, variantName = 'default') {
  const variantKey = String(variantName || 'default').trim() || 'default'
  const markup = String(record?.variants?.[variantKey]?.html || record?.variants?.default?.html || record?.master_html || '').trim()
  return { variantKey, markup }
}

async function replaceSelectedComponentMarkup(markup, options = {}) {
  if (!visualSelectedElement || !visualFrameDocument) return false
  const html = String(markup || '').trim()
  if (!html) return false
  const oldElement = visualSelectedElement
  const oldNodeId = String(visualSelectedId.value || '').trim()
  const oldSelector = oldNodeId ? ensureLayerSelector(oldNodeId, oldElement) : ''
  const oldRow = oldSelector ? visualOverridesMap.value?.[oldSelector] : null
  const preservedStyles = collectPreservedComponentStyles(oldElement, oldRow?.styles || {})
  const oldConstraints = {
    horizontal: String(oldElement.getAttribute(CONSTRAINT_H_ATTR) || '').trim(),
    vertical: String(oldElement.getAttribute(CONSTRAINT_V_ATTR) || '').trim(),
    size: String(oldElement.getAttribute(CONSTRAINT_SIZE_ATTR) || '').trim(),
    sizeWidth: String(oldElement.getAttribute(CONSTRAINT_SIZE_W_ATTR) || '').trim(),
    sizeHeight: String(oldElement.getAttribute(CONSTRAINT_SIZE_H_ATTR) || '').trim(),
  }
  const parent = oldElement.parentElement
  if (!parent) return false
  const anchor = oldElement.nextSibling

  const tpl = visualFrameDocument.createElement('template')
  tpl.innerHTML = html
  const nextElement = tpl.content?.firstElementChild
  if (!nextElement || !isVisualEditableElement(nextElement)) return false

  pushVisualHistorySnapshot({ force: true })
  sanitizeClonedElementTree(nextElement, visualFrameDocument)

  const componentId = String(options.componentId || '').trim()
  const variantName = String(options.variantName || 'default').trim() || 'default'
  if (componentId) {
    nextElement.setAttribute(COMPONENT_INSTANCE_ATTR, componentId)
    nextElement.setAttribute(COMPONENT_MASTER_ATTR, componentId)
    nextElement.setAttribute(COMPONENT_VARIANT_ATTR, variantName)
  }
  if (oldConstraints.horizontal) nextElement.setAttribute(CONSTRAINT_H_ATTR, oldConstraints.horizontal)
  if (oldConstraints.vertical) nextElement.setAttribute(CONSTRAINT_V_ATTR, oldConstraints.vertical)
  if (oldConstraints.size) nextElement.setAttribute(CONSTRAINT_SIZE_ATTR, oldConstraints.size)
  if (oldConstraints.sizeWidth) nextElement.setAttribute(CONSTRAINT_SIZE_W_ATTR, oldConstraints.sizeWidth)
  if (oldConstraints.sizeHeight) nextElement.setAttribute(CONSTRAINT_SIZE_H_ATTR, oldConstraints.sizeHeight)
  for (const [styleKey, styleValue] of Object.entries(preservedStyles)) {
    nextElement.style[styleKey] = String(styleValue || '')
  }

  parent.removeChild(oldElement)
  parent.insertBefore(nextElement, anchor)
  markVisualStructureDirty()

  const nextMap = { ...visualOverridesMap.value }
  if (oldSelector) delete nextMap[oldSelector]
  const nodeId = upsertSingleLayerForElement(nextElement)
  await runVisualLayerScan(visualFrameDocument, { loadToken: previewFrameLoadToken, focusNodeId: nodeId })
  selectVisualLayer(nodeId)
  const selector = ensureLayerSelector(nodeId, nextElement)
  if (selector && Object.keys(preservedStyles).length) {
    const layer = visualLayerIndex.value?.[nodeId]
    nextMap[selector] = {
      selector,
      tag: String(layer?.tag || nextElement.tagName || '').toLowerCase(),
      label: String(layer?.label || nodeLabel(nextElement)),
      styles: { ...preservedStyles },
      apply_text: false,
      text_content: '',
      apply_html: false,
      html_content: '',
    }
  }
  visualOverridesMap.value = nextMap
  componentSwapTarget.value = ''
  return true
}

function createComponentMasterFromSelection() {
  if (!visualSelectedElement) return false
  const currentLayer = visualSelectedLayer.value
  const existingId = String(
    visualSelectedElement.getAttribute(COMPONENT_MASTER_ATTR) ||
    visualSelectedElement.getAttribute(COMPONENT_INSTANCE_ATTR) ||
    ''
  ).trim()
  const componentId = existingId || buildComponentId(currentLayer?.tag || currentLayer?.label || 'component')
  const componentName = String(currentLayer?.label || componentId).trim() || componentId
  const masterHtml = String(visualSelectedElement.outerHTML || '').trim()
  if (!masterHtml) return false

  const next = { ...componentLibrary.value }
  const previous = next[componentId] || { id: componentId, name: componentName, variants: {}, version: 1 }
  const variants = { ...(previous.variants || {}), default: { html: masterHtml } }
  next[componentId] = stampComponentRecord({
    id: componentId,
    name: componentName,
    master_html: masterHtml,
    variants,
    description: String(previous.description || '').trim(),
    published_at: String(previous.published_at || ''),
    version: Number(previous.version || 1),
  }, { bumpVersion: true })
  componentLibrary.value = normalizeComponentLibrary(next)
  visualSelectedElement.setAttribute(COMPONENT_MASTER_ATTR, componentId)
  visualSelectedElement.setAttribute(COMPONENT_INSTANCE_ATTR, componentId)
  visualSelectedElement.setAttribute(COMPONENT_VARIANT_ATTR, selectedComponentVariant.value || 'default')
  markVisualStructureDirty()
  componentSwapTarget.value = ''
  success.value = 'Component master ساخته شد.'
  error.value = ''
  return true
}

function updateComponentMasterFromSelection() {
  if (!visualSelectedElement) return false
  const componentId = String(selectedComponentId.value || '').trim()
  if (!componentId) return false
  const record = componentLibrary.value?.[componentId]
  if (!record) return false
  const variantName = String(selectedComponentVariant.value || 'default').trim() || 'default'
  const markup = String(visualSelectedElement.outerHTML || '').trim()
  if (!markup) return false
  const next = { ...componentLibrary.value }
  next[componentId] = stampComponentRecord({
    ...record,
    master_html: markup,
    variants: { ...(record.variants || {}), [variantName]: { html: markup } },
  }, { bumpVersion: true })
  componentLibrary.value = normalizeComponentLibrary(next)
  success.value = 'Master library به‌روزرسانی شد.'
  error.value = ''
  return true
}

function setActiveLibraryName(value) {
  const next = String(value || '').trim()
  if (!next) return
  activeLibraryName.value = next
}

async function consumeComponentLibraryFromServer(options = {}) {
  const libraryName = String(options?.libraryName || activeLibraryName.value || 'global').trim() || 'global'
  const versionId = String(options?.versionId || '').trim()
  const silent = Boolean(options?.silent)
  error.value = ''
  try {
    const { response, payload } = await postEditorMethodWithFallback('/api/method/mysite.api.consume_management_component_library', {
      library_name: libraryName,
      version_id: versionId,
    })
    if (!response.ok || payload.exception || payload.exc_type) throw new Error(payload?.message || 'دریافت component library از سرور ناموفق بود.')
    const result = payload.message || payload
    const components = normalizeComponentLibrary(result?.components || {})
    if (Object.keys(components).length) {
      componentLibrary.value = normalizeComponentLibrary({ ...(componentLibrary.value || {}), ...components })
    }
    if (!silent) success.value = `Library "${libraryName}" دریافت شد (${Object.keys(components).length} component).`
    const historyRefresh = await postEditorMethodWithFallback('/api/method/mysite.api.get_management_component_library', { library_name: libraryName })
    const historyPayload = historyRefresh.payload?.message || historyRefresh.payload || {}
    if (!historyRefresh.response?.ok || historyRefresh.payload?.exception || historyRefresh.payload?.exc_type) return true
    componentLibrarySummaries.value = Array.isArray(historyPayload.summaries) ? historyPayload.summaries : componentLibrarySummaries.value
    return true
  } catch (err) {
    if (!silent) error.value = err?.message || 'خطا در دریافت library از سرور.'
    return false
  }
}

async function publishComponentLibrary() {
  const next = {}
  for (const [componentId, record] of Object.entries(componentLibrary.value || {})) {
    next[componentId] = stampComponentRecord({ ...(record || {}) }, { publish: true })
  }
  componentLibrary.value = normalizeComponentLibrary(next)
  const payloadJson = JSON.stringify(componentLibrary.value || {}, null, 2)
  const libraryName = String(activeLibraryName.value || 'global').trim() || 'global'
  let publishedVersion = ''
  try {
    const { response, payload } = await postEditorMethodWithFallback('/api/method/mysite.api.publish_management_component_library', {
      library_name: libraryName,
      components: componentLibrary.value,
      note: `manual-publish:${new Date().toISOString()}`,
    })
    if (!response.ok || payload.exception || payload.exc_type) throw new Error(payload?.message || 'publish library با خطا مواجه شد.')
    const result = payload.message || payload
    publishedVersion = String(result?.published_version_id || '').trim()
    componentLibrarySummaries.value = Array.isArray(result?.summaries) ? result.summaries : componentLibrarySummaries.value
  } catch (err) {
    error.value = err?.message || 'publish server library انجام نشد.'
    return false
  }
  try {
    if (navigator?.clipboard?.writeText) await navigator.clipboard.writeText(payloadJson)
  } catch {
    // noop
  }
  success.value = `Library "${libraryName}" publish شد${publishedVersion ? ` (${publishedVersion})` : ''}.`
  error.value = ''
  return true
}

async function createComponentInstance(componentId, variantName = 'default', options = {}) {
  if (!visualFrameDocument?.body) return false
  const id = String(componentId || '').trim()
  if (!id) return false
  const record = componentLibrary.value?.[id]
  if (!record) return false
  const { variantKey, markup } = ensureComponentVariantMarkup(record, variantName)
  if (!markup) return false

  const tpl = visualFrameDocument.createElement('template')
  tpl.innerHTML = markup
  const element = tpl.content?.firstElementChild
  if (!element || !isVisualEditableElement(element)) return false

  pushVisualHistorySnapshot({ force: true })
  sanitizeClonedElementTree(element, visualFrameDocument)
  element.setAttribute(COMPONENT_INSTANCE_ATTR, id)
  element.setAttribute(COMPONENT_MASTER_ATTR, id)
  element.setAttribute(COMPONENT_VARIANT_ATTR, variantKey)
  const dropPoint = options?.point && Number.isFinite(Number(options?.point?.x)) && Number.isFinite(Number(options?.point?.y))
    ? { x: Number(options.point.x), y: Number(options.point.y) }
    : null
  if (dropPoint) {
    element.style.position = 'absolute'
    element.style.left = `${Math.round(dropPoint.x)}px`
    element.style.top = `${Math.round(dropPoint.y)}px`
  }
  const parent = dropPoint ? visualFrameDocument.body : (visualSelectedElement?.parentElement || visualFrameDocument.body)
  const anchor = dropPoint ? null : (visualSelectedElement?.nextSibling || null)
  parent.insertBefore(element, anchor)
  const nodeId = upsertSingleLayerForElement(element)
  selectVisualLayer(nodeId)
  markVisualStructureDirty()
  componentSwapTarget.value = ''
  success.value = 'Instance ساخته شد.'
  error.value = ''
  return true
}

function createVariantFromSelection() {
  if (!visualSelectedElement) return false
  const componentId = String(selectedComponentId.value || '').trim()
  if (!componentId) return false
  const record = componentLibrary.value?.[componentId]
  if (!record) return false
  const variantKey = String(componentVariantDraft.value || '').trim().toLowerCase().replace(/\s+/g, '-') || `variant-${Object.keys(record.variants || {}).length + 1}`
  const markup = String(visualSelectedElement.outerHTML || '').trim()
  if (!markup) return false
  const next = { ...componentLibrary.value }
  const variants = { ...(record.variants || {}), [variantKey]: { html: markup } }
  next[componentId] = stampComponentRecord({ ...record, variants }, { bumpVersion: true })
  componentLibrary.value = normalizeComponentLibrary(next)
  visualSelectedElement.setAttribute(COMPONENT_VARIANT_ATTR, variantKey)
  markVisualStructureDirty()
  componentVariantDraft.value = variantKey
  success.value = 'Variant جدید ذخیره شد.'
  error.value = ''
  return true
}

async function applyVariantToSelection(variantKey) {
  if (!visualSelectedElement || !visualFrameDocument) return false
  const componentId = String(selectedComponentId.value || '').trim()
  if (!componentId) return false
  const record = componentLibrary.value?.[componentId]
  if (!record) return false
  const { variantKey: normalizedVariant, markup } = ensureComponentVariantMarkup(record, variantKey)
  if (!markup) return false
  const replaced = await replaceSelectedComponentMarkup(markup, {
    componentId,
    variantName: normalizedVariant,
  })
  if (!replaced) return false
  success.value = 'Variant اعمال شد.'
  error.value = ''
  return true
}

async function resetComponentOverridesForSelection() {
  const componentId = String(selectedComponentId.value || '').trim()
  if (!componentId) return false
  const record = componentLibrary.value?.[componentId]
  if (!record) return false
  const variantName = String(selectedComponentVariant.value || 'default').trim() || 'default'
  const { variantKey, markup } = ensureComponentVariantMarkup(record, variantName)
  if (!markup) return false
  const replaced = await replaceSelectedComponentMarkup(markup, { componentId, variantName: variantKey })
  if (!replaced) return false
  success.value = 'Overrideهای instance ریست شد.'
  error.value = ''
  return true
}

async function swapComponentInstanceFromSelection() {
  const targetId = String(componentSwapTarget.value || '').trim()
  if (!targetId) return false
  const targetRecord = componentLibrary.value?.[targetId]
  if (!targetRecord) return false
  const requestedVariant = String(selectedComponentVariant.value || 'default').trim() || 'default'
  const { variantKey, markup } = ensureComponentVariantMarkup(targetRecord, requestedVariant)
  if (!markup) return false
  const replaced = await replaceSelectedComponentMarkup(markup, {
    componentId: targetId,
    variantName: variantKey,
  })
  if (!replaced) return false
  success.value = 'Instance با کامپوننت جدید جایگزین شد.'
  error.value = ''
  return true
}

function detachComponentInstanceFromSelection() {
  const elements = getSelectedElementsInDomOrder()
  if (!elements.length) return false
  pushVisualHistorySnapshot({ force: true })
  let detached = false
  for (const element of elements) {
    if (
      element.hasAttribute(COMPONENT_INSTANCE_ATTR) ||
      element.hasAttribute(COMPONENT_MASTER_ATTR) ||
      element.hasAttribute(COMPONENT_VARIANT_ATTR)
    ) detached = true
    element.removeAttribute(COMPONENT_INSTANCE_ATTR)
    element.removeAttribute(COMPONENT_MASTER_ATTR)
    element.removeAttribute(COMPONENT_VARIANT_ATTR)
  }
  if (detached) markVisualStructureDirty()
  componentSwapTarget.value = ''
  success.value = 'Instance از library جدا شد.'
  error.value = ''
  return true
}

function selectNestedInstanceNode(nodeId) {
  const id = String(nodeId || '').trim()
  if (!id || !visualFrameDocument) return
  const element = getVisualElementById(id)
  if (!element) return
  if (!visualLayerIndex.value[id]) {
    upsertSingleLayerForElement(element)
    void runVisualLayerScan(visualFrameDocument, { loadToken: previewFrameLoadToken, focusNodeId: id })
  }
  selectVisualLayer(id)
}

function applyConstraint(axis, mode, options = {}) {
  const selectedIds = Array.isArray(visualSelectedIds.value) && visualSelectedIds.value.length
    ? [...visualSelectedIds.value]
    : (visualSelectedId.value ? [visualSelectedId.value] : [])
  if (!selectedIds.length) return false
  const targetAxis = String(axis || '').trim()
  const targetMode = String(mode || '').trim()
  if (!targetAxis || !targetMode) return false

  const applySizeMode = (element, applyStyle, dimension, sizeMode) => {
    const targetDimension = String(dimension || '').trim()
    const modeValue = String(sizeMode || '').trim()
    if (!targetDimension || !modeValue) return
    const isWidth = targetDimension === 'width'
    const isHeight = targetDimension === 'height'
    if (!isWidth && !isHeight) return
    const styleKey = isWidth ? 'width' : 'height'
    const minStyleKey = isWidth ? 'minWidth' : 'minHeight'

    if (modeValue === 'fixed') {
      const rect = element.getBoundingClientRect()
      const pxValue = isWidth ? Math.max(1, Math.round(rect.width)) : Math.max(1, Math.round(rect.height))
      applyStyle(styleKey, `${pxValue}px`)
      return
    }

    if (modeValue === 'hug') {
      applyStyle(styleKey, 'fit-content')
      if (isHeight) applyStyle(minStyleKey, '')
      return
    }

    if (modeValue === 'fill') {
      const parent = element.parentElement
      const win = element.ownerDocument?.defaultView
      const parentComputed = parent && win?.getComputedStyle ? win.getComputedStyle(parent) : null
      const parentDisplay = String(parentComputed?.display || (parent ? parent.style.display : '') || '').trim().toLowerCase()
      if (parentDisplay === 'flex') {
        const direction = String(parentComputed?.flexDirection || (parent ? parent.style.flexDirection : '') || '').trim().toLowerCase()
        const isRow = !direction || direction.startsWith('row')
        const mainAxisIsWidth = isRow
        if ((mainAxisIsWidth && isWidth) || (!mainAxisIsWidth && isHeight)) {
          applyStyle('flexGrow', '1')
          applyStyle('flexShrink', '1')
          applyStyle(styleKey, '')
          return
        }
      }
      applyStyle(styleKey, '100%')
      return
    }
  }

  if (!options?.skipHistory) pushVisualHistorySnapshot({ force: true })
  const map = { ...visualOverridesMap.value }
  for (const nodeId of selectedIds) {
    const element = getVisualElementById(nodeId)
    const layer = visualLayerIndex.value?.[nodeId]
    if (!element || !layer) continue
    if (isLayerLockedElement(element)) continue
    const selector = ensureLayerSelector(nodeId, element)
    if (!selector) continue
    const row = map[selector]
      ? { ...map[selector], styles: { ...(map[selector].styles || {}) } }
      : { selector, tag: layer.tag, label: layer.label, styles: {}, apply_text: false, text_content: '', apply_html: false, html_content: '' }

    const applyStyle = (key, value) => {
      const styleKey = String(key || '').trim()
      const styleValue = String(value ?? '').trim()
      if (!styleKey) return
      if (styleValue) {
        row.styles[styleKey] = styleValue
        element.style[styleKey] = styleValue
      } else {
        delete row.styles[styleKey]
        element.style[styleKey] = ''
      }
      if (nodeId === visualSelectedId.value) visualProps.value[styleKey] = styleValue
    }

    if (targetAxis === 'horizontal') {
      element.setAttribute(CONSTRAINT_H_ATTR, targetMode)
      if (targetMode === 'left') {
        applyStyle('alignSelf', 'flex-start')
        applyStyle('marginLeft', '0')
        applyStyle('marginRight', 'auto')
      } else if (targetMode === 'center') {
        applyStyle('alignSelf', 'center')
        applyStyle('marginLeft', 'auto')
        applyStyle('marginRight', 'auto')
      } else if (targetMode === 'right') {
        applyStyle('alignSelf', 'flex-end')
        applyStyle('marginLeft', 'auto')
        applyStyle('marginRight', '0')
      } else if (targetMode === 'stretch') {
        applyStyle('alignSelf', 'stretch')
        applyStyle('width', '100%')
      }
    } else if (targetAxis === 'vertical') {
      element.setAttribute(CONSTRAINT_V_ATTR, targetMode)
      if (targetMode === 'top') {
        applyStyle('marginTop', '0')
        applyStyle('marginBottom', 'auto')
      } else if (targetMode === 'center') {
        applyStyle('marginTop', 'auto')
        applyStyle('marginBottom', 'auto')
      } else if (targetMode === 'bottom') {
        applyStyle('marginTop', 'auto')
        applyStyle('marginBottom', '0')
      } else if (targetMode === 'stretch') {
        applyStyle('height', '100%')
      }
    } else if (targetAxis === 'size') {
      element.setAttribute(CONSTRAINT_SIZE_ATTR, targetMode)
      element.setAttribute(CONSTRAINT_SIZE_W_ATTR, targetMode)
      element.setAttribute(CONSTRAINT_SIZE_H_ATTR, targetMode)
      applySizeMode(element, applyStyle, 'width', targetMode)
      applySizeMode(element, applyStyle, 'height', targetMode)
    } else if (targetAxis === 'size-width') {
      element.setAttribute(CONSTRAINT_SIZE_W_ATTR, targetMode)
      applySizeMode(element, applyStyle, 'width', targetMode)
    } else if (targetAxis === 'size-height') {
      element.setAttribute(CONSTRAINT_SIZE_H_ATTR, targetMode)
      applySizeMode(element, applyStyle, 'height', targetMode)
    }

    const modeW = String(element.getAttribute(CONSTRAINT_SIZE_W_ATTR) || '').trim()
    const modeH = String(element.getAttribute(CONSTRAINT_SIZE_H_ATTR) || '').trim()
    if (modeW && modeH && modeW === modeH) element.setAttribute(CONSTRAINT_SIZE_ATTR, modeW)
    else element.removeAttribute(CONSTRAINT_SIZE_ATTR)

    if (!row.apply_text && !row.apply_html && !Object.keys(row.styles || {}).length) delete map[selector]
    else map[selector] = row
  }
  visualOverridesMap.value = map
  markVisualStructureDirty()
  success.value = 'Constraint اعمال شد.'
  error.value = ''
  return true
}

function applyConstraintAnchor(anchorId) {
  const key = String(anchorId || '').trim().toLowerCase()
  const matrix = {
    'top-left': { horizontal: 'left', vertical: 'top' },
    'top-center': { horizontal: 'center', vertical: 'top' },
    'top-right': { horizontal: 'right', vertical: 'top' },
    'center-left': { horizontal: 'left', vertical: 'center' },
    center: { horizontal: 'center', vertical: 'center' },
    'center-right': { horizontal: 'right', vertical: 'center' },
    'bottom-left': { horizontal: 'left', vertical: 'bottom' },
    'bottom-center': { horizontal: 'center', vertical: 'bottom' },
    'bottom-right': { horizontal: 'right', vertical: 'bottom' },
  }
  const target = matrix[key]
  if (!target) return false
  const horizontalOk = applyConstraint('horizontal', target.horizontal)
  const verticalOk = applyConstraint('vertical', target.vertical, { skipHistory: true })
  return Boolean(horizontalOk || verticalOk)
}

function addRawStyleRule() {
  if (!visualSelectedLayer.value) return
  const selectedProperty = String(rawStyleDraft.value.property || '').trim()
  const propertyName = selectedProperty === '__custom__'
    ? String(rawStyleDraft.value.customProperty || '').trim()
    : selectedProperty
  const styleValue = String(rawStyleDraft.value.value || '').trim()
  if (!propertyName || !styleValue) return
  const normalizedProperty = selectedProperty === '__custom__'
    ? propertyName
    : toStyleObjectKey(propertyName)
  applyVisualField(normalizedProperty, styleValue)
  rawStyleDraft.value.value = ''
  if (selectedProperty === '__custom__') rawStyleDraft.value.customProperty = ''
}

function removeRawStyleRule(styleKey) {
  if (!styleKey) return
  applyVisualField(String(styleKey), '')
}

async function applyRawHtmlToSelected() {
  if (!visualSelectedElement || !visualFrameDocument) return
  pushVisualHistorySnapshot({ force: true })
  const html = String(rawHtmlInput.value || '')
  visualSelectedElement.innerHTML = html
  markVisualStructureDirty()
  const selectedId = String(visualSelectedId.value || '').trim()
  if (selectedId) {
    const selector = ensureLayerSelector(selectedId, visualSelectedElement)
    const layer = visualLayerIndex.value?.[selectedId]
    if (selector) {
      const map = { ...visualOverridesMap.value }
      const existing = map[selector]
        ? { ...map[selector], styles: { ...(map[selector].styles || {}) } }
        : { selector, tag: layer?.tag || '', label: layer?.label || '', styles: {}, apply_text: false, text_content: '', apply_html: false, html_content: '' }
      if (html.trim()) {
        existing.apply_text = false
        existing.text_content = ''
        existing.apply_html = true
        existing.html_content = html
      } else {
        existing.apply_text = true
        existing.text_content = ''
        existing.apply_html = false
        existing.html_content = ''
      }
      if (!existing.apply_text && !existing.apply_html && !Object.keys(existing.styles || {}).length) delete map[selector]
      else map[selector] = existing
      visualOverridesMap.value = map
    }
  }
  await runVisualLayerScan(visualFrameDocument, {
    loadToken: previewFrameLoadToken,
    focusNodeId: selectedId,
  })
  if (selectedId) selectVisualLayer(selectedId)
  success.value = 'Raw HTML اعمال شد.'
  error.value = ''
}

function formatDate(value) {
  if (!value) return '-'
  const dt = new Date(value)
  if (Number.isNaN(dt.getTime())) return value
  return dt.toLocaleString('fa-IR')
}

function parseRouteFromQuery() {
  const params = new URLSearchParams(window.location.search)
  route.value = normalizeEditorRoute(params.get('route'))
  const nextTarget = String(params.get('target_file') || '').trim()
  if (nextTarget) selectedTargetFile.value = nextTarget
}

function cssEscape(value) {
  const raw = String(value || '')
  if (window.CSS && typeof window.CSS.escape === 'function') return window.CSS.escape(raw)
  return raw.replace(/[^a-zA-Z0-9_-]/g, (char) => `\\${char}`)
}

function normalizeVisualOverrideItem(row) {
  const selector = String(row?.selector || '').trim()
  if (!selector) return null
  const styles = {}
  const rawStyles = row?.styles
  if (rawStyles && typeof rawStyles === 'object' && !Array.isArray(rawStyles)) {
    for (const [rawKey, rawValue] of Object.entries(rawStyles)) {
      const key = String(rawKey || '').trim()
      const value = String(rawValue || '').trim()
      if (!key || !value) continue
      styles[key] = value
    }
  }
  const applyText = Boolean(row?.apply_text)
  const textContent = String(row?.text_content ?? '')
  const applyHtml = Boolean(row?.apply_html)
  const htmlContent = String(row?.html_content ?? '')
  if (!Object.keys(styles).length && !applyText && !applyHtml) return null
  return {
    selector,
    tag: String(row?.tag || '').trim(),
    label: String(row?.label || '').trim(),
    styles,
    apply_text: applyText,
    text_content: applyText ? textContent : '',
    apply_html: applyHtml,
    html_content: applyHtml ? htmlContent : '',
  }
}

function stableJson(value) {
  if (Array.isArray(value)) return `[${value.map((item) => stableJson(item)).join(',')}]`
  if (value && typeof value === 'object') {
    const entries = Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([key, val]) => `${JSON.stringify(key)}:${stableJson(val)}`)
    return `{${entries.join(',')}}`
  }
  return JSON.stringify(value ?? null)
}

function cloneOverridesMap(value) {
  try {
    return JSON.parse(JSON.stringify(value || {}))
  } catch {
    return {}
  }
}

function createVisualSnapshotSignature(snapshot) {
  if (!snapshot) return ''
  return `${String(snapshot.body_html || '')}||${stableJson(snapshot.overrides || {})}||${String(snapshot.raw_css || '')}||${stableJson(snapshot.token_collections || {})}||${String(snapshot.token_active_collection || '')}||${String(snapshot.token_active_mode || '')}||${String(snapshot.selected_id || '')}`
}

function createVisualSnapshot() {
  if (!visualFrameDocument?.body) return null
  const snapshot = {
    body_html: String(visualFrameDocument.body.innerHTML || ''),
    overrides: cloneOverridesMap(visualOverridesMap.value),
    raw_css: String(rawCss.value || ''),
    token_collections: cloneTokenCollections(tokenCollections.value),
    token_active_collection: String(activeTokenCollectionId.value || ''),
    token_active_mode: String(activeTokenMode.value || 'light'),
    selected_id: String(visualSelectedId.value || ''),
  }
  snapshot.signature = createVisualSnapshotSignature(snapshot)
  return snapshot
}

function pushVisualHistorySnapshot(options = {}) {
  if (visualRestoringHistory) return false
  const snapshot = createVisualSnapshot()
  if (!snapshot) return false
  const force = Boolean(options?.force)
  const clearRedo = options?.clearRedo !== false
  const now = Date.now()
  if (!force && now - visualLastHistoryPushAt < 220) return false
  const last = visualUndoStack[visualUndoStack.length - 1]
  if (last?.signature === snapshot.signature) return false
  visualUndoStack.push(snapshot)
  if (visualUndoStack.length > MAX_VISUAL_HISTORY_ITEMS) visualUndoStack.shift()
  visualLastHistoryPushAt = now
  if (clearRedo) visualRedoStack = []
  return true
}

async function restoreVisualSnapshot(snapshot) {
  if (!snapshot || !visualFrameDocument?.body) return false
  visualRestoringHistory = true
  try {
    visualFrameDocument.body.innerHTML = String(snapshot.body_html || '')
    visualOverridesMap.value = cloneOverridesMap(snapshot.overrides)
    rawCss.value = String(snapshot.raw_css || '')
    {
      const selection = resolveActiveTokenSelection(
        snapshot.token_collections,
        String(snapshot.token_active_collection || ''),
        String(snapshot.token_active_mode || 'light')
      )
      tokenCollections.value = selection.collections
      activeTokenCollectionId.value = selection.collectionId
      activeTokenMode.value = selection.mode
    }
    applyRawCssToDocument(visualFrameDocument)
    applyActiveTokenModeToDocument(visualFrameDocument)
    collectPreviewCssVariables(visualFrameDocument)
    const focusNodeId = String(snapshot.selected_id || '')
    await runVisualLayerScan(visualFrameDocument, { loadToken: previewFrameLoadToken, focusNodeId: focusNodeId || '' })
    if (!focusNodeId) clearVisualSelection()
    markVisualStructureDirty()
  } finally {
    visualRestoringHistory = false
  }
  return true
}

async function undoVisualChange() {
  if (!visualUndoStack.length || !visualFrameDocument?.body) return false
  const current = createVisualSnapshot()
  const snapshot = visualUndoStack.pop()
  if (current) {
    visualRedoStack.push(current)
    if (visualRedoStack.length > MAX_VISUAL_HISTORY_ITEMS) visualRedoStack.shift()
  }
  const restored = await restoreVisualSnapshot(snapshot)
  if (restored) {
    success.value = 'Undo انجام شد.'
    error.value = ''
  }
  return restored
}

async function redoVisualChange() {
  if (!visualRedoStack.length || !visualFrameDocument?.body) return false
  const current = createVisualSnapshot()
  const snapshot = visualRedoStack.pop()
  if (current) {
    visualUndoStack.push(current)
    if (visualUndoStack.length > MAX_VISUAL_HISTORY_ITEMS) visualUndoStack.shift()
  }
  const restored = await restoreVisualSnapshot(snapshot)
  if (restored) {
    success.value = 'Redo انجام شد.'
    error.value = ''
  }
  return restored
}

function computeVisualSignature() {
  const rows = Object.values(visualOverridesMap.value || {})
    .filter((row) => {
      if (!row || typeof row !== 'object') return false
      const styles = row.styles && typeof row.styles === 'object' ? row.styles : {}
      return Object.keys(styles).length > 0 || Boolean(row.apply_text) || Boolean(row.apply_html)
    })
    .map((row) => ({
      selector: String(row.selector || '').trim(),
      tag: String(row.tag || '').trim(),
      label: String(row.label || '').trim(),
      apply_text: Boolean(row.apply_text),
      text_content: row.apply_text ? String(row.text_content ?? '') : '',
      apply_html: Boolean(row.apply_html),
      html_content: row.apply_html ? String(row.html_content ?? '') : '',
      styles: row.styles && typeof row.styles === 'object' ? { ...row.styles } : {},
    }))
    .sort((a, b) => a.selector.localeCompare(b.selector))
  const tokenSelection = resolveActiveTokenSelection(
    tokenCollections.value,
    activeTokenCollectionId.value,
    activeTokenMode.value
  )
  return stableJson({
    rows,
    raw_css: String(rawCss.value || ''),
    active_branch: String(activeBranch.value || DEFAULT_EDITOR_BRANCH),
    prototype_model: normalizePrototypeModel(prototypeModel.value),
    token_collections: tokenSelection.collections,
    token_active_collection: tokenSelection.collectionId,
    token_active_mode: tokenSelection.mode,
  })
}

function computeSourceSignature() {
  return String(sourceCode.value || '')
}

// ⚡ PERFORMANCE FIX: Debounced dirty state recomputation
function scheduleDirtyRecompute() {
  if (dirtyDebounceTimer !== null) {
    window.clearTimeout(dirtyDebounceTimer)
  }
  dirtyDebounceTimer = window.setTimeout(() => {
    dirtyDebounceTimer = null
    visualDirty.value = visualStructureDirty.value || computeVisualSignature() !== baselineVisualSignature.value
    sourceDirty.value = computeSourceSignature() !== baselineSourceSignature.value
    if (visualDirty.value || sourceDirty.value) scheduleCrashRecoveryPersist()
    else clearCrashRecoverySnapshot()
  }, 300)
}

function recomputeDirtyState() {
  scheduleDirtyRecompute()
}

function setDirtyBaselineFromCurrentState() {
  if (dirtyDebounceTimer !== null) {
    window.clearTimeout(dirtyDebounceTimer)
    dirtyDebounceTimer = null
  }
  baselineVisualSignature.value = computeVisualSignature()
  baselineSourceSignature.value = computeSourceSignature()
  visualStructureDirty.value = false
  visualDirty.value = false
  sourceDirty.value = false
  clearCrashRecoverySnapshot()
}

function hasUnsavedChanges() {
  return visualDirty.value || sourceDirty.value
}

function clearAutoSaveTimer() {
  if (autoSaveTimer !== null) {
    window.clearTimeout(autoSaveTimer)
    autoSaveTimer = null
  }
}

function cancelAutoSave() {
  clearAutoSaveTimer()
  autoSavePending.value = false
}

function canAutoSave() {
  if (!autoSaveEnabled.value) return false
  if (!hasEditorTarget.value) return false
  if (loading.value || savingVisual.value || savingSource.value) return false
  if (restoringVersionId.value) return false
  return true
}

function scheduleAutoSave(delayMs = AUTO_SAVE_DEBOUNCE_MS) {
  if (!autoSaveEnabled.value) return
  if (!hasEditorTarget.value || !hasUnsavedChanges()) {
    cancelAutoSave()
    return
  }
  autoSavePending.value = true
  clearAutoSaveTimer()
  const waitMs = Math.max(500, Number(delayMs || AUTO_SAVE_DEBOUNCE_MS))
  autoSaveTimer = window.setTimeout(() => {
    autoSaveTimer = null
    void runAutoSaveNow()
  }, waitMs)
}

async function runAutoSaveNow() {
  if (!autoSaveEnabled.value) { cancelAutoSave(); return }
  if (!hasEditorTarget.value || !hasUnsavedChanges()) {
    autoSavePending.value = false
    autoSaveRetryCount = 0
    return
  }
  if (!canAutoSave()) {
    scheduleAutoSave(Math.max(AUTO_SAVE_DEBOUNCE_MS, 900))
    return
  }

  autoSavePending.value = false
  autoSaveRunning.value = true
  let allSaved = true
  try {
    if (sourceDirty.value) {
      const ok = await saveSourceCode({ auto: true, skipReload: true, silentSuccess: true })
      if (!ok) allSaved = false
    }
    if (visualDirty.value) {
      const ok = await saveVisualChanges({ auto: true, skipReload: true, silentSuccess: true })
      if (!ok) allSaved = false
    }
  } finally {
    autoSaveRunning.value = false
  }

  if (allSaved && !hasUnsavedChanges()) {
    autoSaveRetryCount = 0
    return
  }

  if (!allSaved) {
    autoSaveRetryCount += 1
    if (autoSaveRetryCount <= AUTO_SAVE_MAX_RETRIES && hasUnsavedChanges()) {
      scheduleAutoSave(AUTO_SAVE_RETRY_DELAY_MS)
    } else {
      autoSavePending.value = false
    }
    return
  }

  autoSaveRetryCount = 0
  if (hasUnsavedChanges()) scheduleAutoSave(AUTO_SAVE_DEBOUNCE_MS)
}

function confirmDiscardChanges() {
  if (!hasUnsavedChanges()) return true
  return window.confirm('تغییرات ذخیره‌نشده دارید. ادامه می‌دهید؟')
}

function handleBeforeUnload(event) {
  if (!hasUnsavedChanges()) return
  persistCrashRecoverySnapshotNow()
  event.preventDefault()
  event.returnValue = ''
}

function isSourceEditorFocused() {
  return Boolean(sourceCodeTextarea.value && document.activeElement === sourceCodeTextarea.value)
}

function matchShortcutKey(event, letter) {
  const key = String(event?.key || '').toLowerCase()
  const code = String(event?.code || '').toLowerCase()
  const target = String(letter || '').trim().toLowerCase()
  if (!target) return false
  return key === target || code === `key${target}`
}

function handleEditorKeydown(event, options = {}) {
  const fromFrame = Boolean(options?.fromFrame)
  const key = String(event.key || '').toLowerCase()
  const code = String(event.code || '')
  const hasPrimaryModifier = Boolean(event.ctrlKey || event.metaKey)
  const typing = isTypingTarget(event.target)

  if (code === 'Space' && !typing) {
    canvasSpacePressed = true
    event.preventDefault()
  }

  if (!typing && event.shiftKey && code === 'Digit1') {
    event.preventDefault()
    fitCanvasZoomToViewport()
    return
  }

  if (!typing && event.shiftKey && code === 'Digit2') {
    event.preventDefault()
    resetCanvasZoom()
    return
  }

  if (hasPrimaryModifier && matchShortcutKey(event, 's')) {
    event.preventDefault()
    if (loading.value || savingVisual.value || savingSource.value) return
    if (!fromFrame && isSourceEditorFocused()) { void saveSourceCode(); return }
    void saveVisualChanges()
    return
  }

  if (hasPrimaryModifier && matchShortcutKey(event, 'd')) {
    event.preventDefault()
    if (typing) return
    duplicateSelectedElement()
    return
  }

  if (hasPrimaryModifier && matchShortcutKey(event, 'z')) {
    if (typing) return
    event.preventDefault()
    if (event.shiftKey) { void redoVisualChange(); return }
    void undoVisualChange()
    return
  }

  if (hasPrimaryModifier && matchShortcutKey(event, 'y')) {
    if (typing) return
    event.preventDefault()
    void redoVisualChange()
    return
  }

  if (hasPrimaryModifier && matchShortcutKey(event, 'c')) {
    if (typing || !visualSelectedElement) return
    event.preventDefault()
    void copySelectedElementToClipboard()
    return
  }

  if (hasPrimaryModifier && matchShortcutKey(event, 'g')) {
    if (typing) return
    event.preventDefault()
    if (event.shiftKey) { void ungroupSelectedElements(); return }
    void groupSelectedElements()
    return
  }

  if (hasPrimaryModifier && matchShortcutKey(event, 'v')) {
    if (typing) return
    event.preventDefault()
    void pasteClipboardElement()
    return
  }

  if (hasPrimaryModifier) return

  if (typing) return

  if (event.shiftKey && matchShortcutKey(event, 'd') && !hasPrimaryModifier) {
    event.preventDefault()
    duplicateSelectedElement()
    return
  }

  if (key === 'escape') {
    clearVisualSelection()
    return
  }

  if (key === 'delete' || key === 'backspace') {
    event.preventDefault()
    void deleteSelectedElement()
    return
  }

  if (matchShortcutKey(event, 'v')) { setActiveTool('select'); return }
  if (matchShortcutKey(event, 'f')) { setActiveTool('frame'); return }
  if (matchShortcutKey(event, 'r')) { setActiveTool('rectangle'); return }
  if (matchShortcutKey(event, 't')) { setActiveTool('text'); return }
  if (matchShortcutKey(event, 'c')) { setActiveTool('component'); return }
  if (matchShortcutKey(event, 'k')) { setActiveTool('comment'); return }
  if (matchShortcutKey(event, 'p')) { setActiveTool('pen'); return }

  const step = event.shiftKey
    ? Math.max(1, Number(nudgeStepLarge.value || 10))
    : Math.max(1, Number(nudgeStep.value || 1))
  if (key === 'arrowup') { event.preventDefault(); nudgeSelectedElement(0, -step); return }
  if (key === 'arrowdown') { event.preventDefault(); nudgeSelectedElement(0, step); return }
  if (key === 'arrowleft') { event.preventDefault(); nudgeSelectedElement(-step, 0); return }
  if (key === 'arrowright') { event.preventDefault(); nudgeSelectedElement(step, 0) }
}

function handleGlobalKeydown(event) {
  handleEditorKeydown(event, { fromFrame: false })
}

function handleGlobalKeyup(event) {
  const code = String(event?.code || '')
  if (code === 'Space') canvasSpacePressed = false
}

function resetVisualProps() {
  for (const key of Object.keys(visualProps.value)) visualProps.value[key] = ''
  customFieldMode.value = {}
}

function expandLayerAncestors(nodeId) {
  const key = String(nodeId || '').trim()
  if (!key) return
  const index = visualLayerIndex.value || {}
  let changed = false
  let current = index?.[key]
  while (current) {
    const parentId = String(current.parent_id || '').trim()
    if (!parentId) break
    if (!visualExpandedMap.value[parentId]) {
      visualExpandedMap.value[parentId] = true
      changed = true
    }
    current = index?.[parentId]
  }
  if (changed) triggerRef(visualExpandedMap)
}

function getSelectedElements() {
  const ids = Array.isArray(visualSelectedIds.value) ? visualSelectedIds.value : []
  if (!ids.length) return []
  return ids.map((nodeId) => getVisualElementById(nodeId)).filter(Boolean)
}

function getSelectedElementsInDomOrder() {
  const elements = getSelectedElements()
  return elements.sort((a, b) => {
    if (a === b) return 0
    const pos = a.compareDocumentPosition(b)
    if (pos & Node.DOCUMENT_POSITION_FOLLOWING) return -1
    if (pos & Node.DOCUMENT_POSITION_PRECEDING) return 1
    return 0
  })
}

function applySelectionClasses() {
  if (!visualFrameDocument?.body) return
  for (const row of Array.from(visualFrameDocument.querySelectorAll('.mysite-visual-selected, .mysite-visual-selected-secondary'))) {
    row.classList.remove('mysite-visual-selected')
    row.classList.remove('mysite-visual-selected-secondary')
  }
  const ids = Array.isArray(visualSelectedIds.value) ? visualSelectedIds.value : []
  const primary = String(visualSelectedId.value || '').trim()
  for (const nodeId of ids) {
    const element = getVisualElementById(nodeId)
    if (!element) continue
    element.classList.add(nodeId === primary ? 'mysite-visual-selected' : 'mysite-visual-selected-secondary')
  }
}

function clearVisualSelection() {
  void finishInlineTextEditing(true)
  if (visualFrameDocument?.body) {
    for (const row of Array.from(visualFrameDocument.querySelectorAll('.mysite-visual-selected, .mysite-visual-selected-secondary'))) {
      row.classList.remove('mysite-visual-selected')
      row.classList.remove('mysite-visual-selected-secondary')
    }
  }
  visualSelectedElement = null
  visualSelectedId.value = ''
  visualSelectedIds.value = []
  rawHtmlInput.value = ''
  resetVisualProps()
  hideResizeOverlay()
  hideMeasureOverlay()
  hideRedlineOverlay()
  syncPrototypeDraftFromSelection()
}

function resetVisualLayerState() {
  visualLayers.value = []
  visualLayerIndex.value = {}
  visualChildrenMap.value = {}
  visualExpandedMap.value = {}
  // rowRefs will self-clean via :ref callbacks
}

function upsertSingleLayerForElement(element) {
  if (!isVisualEditableElement(element)) return ''
  const nodeId = ensureVisualNodeId(element)
  // If already in index, just return the id (no-op)
  if (visualLayerIndex.value[nodeId]) return nodeId

  let parentId = ''
  let parent = element.parentElement
  while (parent && parent !== visualFrameDocument?.body) {
    if (!isVisualEditableElement(parent)) {
      parent = parent.parentElement
      continue
    }
    const candidateId = String(parent.getAttribute(VISUAL_NODE_ATTR) || '').trim()
    if (candidateId) {
      parentId = candidateId
      break
    }
    parent = parent.parentElement
  }
  if (parentId && !visualLayerIndex.value[parentId]) parentId = ''

  const parentDepth = parentId ? Number(visualLayerIndex.value?.[parentId]?.depth || 0) : -1
  const childCount = Array.from(element.children || []).reduce(
    (count, child) => (count + (isVisualEditableElement(child) ? 1 : 0)),
    0
  )

  const layer = {
    id: nodeId, depth: Math.max(0, parentDepth + 1), parent_id: parentId, tag: String(element.tagName || '').toLowerCase(),
    label: nodeLabel(element), selector: String(buildCssSelector(element) || '').trim(),
    original_text: _quickTextOf(element), child_count: childCount,
    ...buildLayerMetaForElement(element, childCount),
  }
  // ⚡ Direct mutation, single triggerRef each
  visualLayerIndex.value[nodeId] = layer
  visualLayers.value.push(layer)
  const bucketKey = parentId || '__root__'
  if (!Array.isArray(visualChildrenMap.value[bucketKey])) visualChildrenMap.value[bucketKey] = []
  if (!visualChildrenMap.value[bucketKey].includes(nodeId)) visualChildrenMap.value[bucketKey].push(nodeId)
  if (parentId && visualLayerIndex.value[parentId]) {
    visualLayerIndex.value[parentId].child_count = (visualChildrenMap.value[parentId] || []).length
    if (!Object.prototype.hasOwnProperty.call(visualExpandedMap.value, parentId)) {
      visualExpandedMap.value[parentId] = true
      triggerRef(visualExpandedMap)
    }
  }
  triggerRef(visualLayerIndex)
  triggerRef(visualLayers)
  triggerRef(visualChildrenMap)
  return nodeId
}

function focusLayerRow(nodeId) {
  const key = String(nodeId || '').trim()
  if (!key) return
  nextTick(() => {
    const el = visualLayerRowRefs.value?.[key]
    if (!el || typeof el.scrollIntoView !== 'function') return
    el.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  })
}

async function onLayerDrop(payload) {
  const draggedId = String(payload?.draggedId || '').trim()
  const targetId = String(payload?.targetId || '').trim()
  if (!draggedId || !targetId || draggedId === targetId) return
  if (!visualFrameDocument) return

  const draggedElement = getVisualElementById(draggedId)
  const targetElement = getVisualElementById(targetId)
  if (!draggedElement || !targetElement) return
  if (draggedElement === targetElement) return
  if (draggedElement.contains(targetElement)) return

  const parent = targetElement.parentElement
  if (!parent) return

  pushVisualHistorySnapshot({ force: true })
  parent.insertBefore(draggedElement, targetElement)
  markVisualStructureDirty()
  await runVisualLayerScan(visualFrameDocument, { loadToken: previewFrameLoadToken, focusNodeId: draggedId })
  selectVisualLayer(draggedId)
  success.value = 'ترتیب لایه به‌روزرسانی شد.'
}

function syncLayerMetaFromElement(nodeId, element = null) {
  const key = String(nodeId || '').trim()
  if (!key) return
  const layer = visualLayerIndex.value?.[key]
  const target = isVisualEditableElement(element) ? element : getVisualElementById(key)
  if (!layer || !target) return
  const childCount = Math.max(0, Number(layer.child_count || 0))
  Object.assign(layer, buildLayerMetaForElement(target, childCount))
  layer.label = nodeLabel(target)
  triggerRef(visualLayerIndex)
  triggerRef(visualLayers)
}

function renameVisualLayer(payload) {
  const nodeId = String(payload?.id || '').trim()
  if (!nodeId) return
  const layer = visualLayerIndex.value?.[nodeId]
  if (!layer) return
  const nextValue = String(payload?.value || '').trim().slice(0, 140)
  const element = getVisualElementById(nodeId)
  if (element) {
    if (nextValue) element.setAttribute(LAYER_LABEL_ATTR, nextValue)
    else element.removeAttribute(LAYER_LABEL_ATTR)
    markVisualStructureDirty()
  }
  layer.label = nextValue || (element ? nodeLabel(element) : String(layer.label || layer.tag || nodeId))
  const selector = element ? ensureLayerSelector(nodeId, element) : String(layer.selector || '').trim()
  if (selector && visualOverridesMap.value?.[selector]) {
    const map = { ...visualOverridesMap.value }
    map[selector] = { ...map[selector], label: layer.label }
    visualOverridesMap.value = map
  }
  triggerRef(visualLayerIndex)
  triggerRef(visualLayers)
  success.value = 'نام لایه به‌روزرسانی شد.'
}

function toggleLayerVisibility(nodeId) {
  const key = String(nodeId || '').trim()
  if (!key) return
  const element = getVisualElementById(key)
  if (!element) return
  pushVisualHistorySnapshot({ force: true })
  const hiddenNow = hasLayerFlagAttr(element, LAYER_HIDDEN_ATTR) || String(element.style.display || '').trim().toLowerCase() === 'none'
  if (hiddenNow) {
    const previousDisplay = String(element.getAttribute(LAYER_PREV_DISPLAY_ATTR) || '')
    if (previousDisplay && previousDisplay !== '__empty__') element.style.display = previousDisplay
    else element.style.removeProperty('display')
    element.removeAttribute(LAYER_HIDDEN_ATTR)
    element.removeAttribute(LAYER_PREV_DISPLAY_ATTR)
    success.value = 'لایه نمایش داده شد.'
  } else {
    const previousDisplay = String(element.style.display || '').trim()
    element.setAttribute(LAYER_PREV_DISPLAY_ATTR, previousDisplay || '__empty__')
    element.style.display = 'none'
    element.setAttribute(LAYER_HIDDEN_ATTR, '1')
    success.value = 'لایه مخفی شد.'
  }
  markVisualStructureDirty()
  syncLayerMetaFromElement(key, element)
  if (!hiddenNow && visualSelectedIds.value.includes(key)) {
    const nextIds = visualSelectedIds.value.filter((row) => String(row || '').trim() !== key)
    if (!nextIds.length) {
      clearVisualSelection()
    } else {
      const nextPrimary = nextIds.includes(visualSelectedId.value) ? visualSelectedId.value : nextIds[nextIds.length - 1]
      visualSelectedIds.value = [...nextIds]
      visualSelectedId.value = String(nextPrimary || '')
      visualSelectedElement = getVisualElementById(visualSelectedId.value)
      applySelectionClasses()
      if (visualSelectedElement) syncVisualPropsFromElement(visualSelectedElement)
      else resetVisualProps()
      syncPrototypeDraftFromSelection()
    }
  }
  nextTick(() => { syncResizeOverlay(); syncRedlineOverlay() })
}

function toggleLayerLock(nodeId) {
  const key = String(nodeId || '').trim()
  if (!key) return
  const element = getVisualElementById(key)
  if (!element) return
  pushVisualHistorySnapshot({ force: true })
  const lockedNow = hasLayerFlagAttr(element, LAYER_LOCKED_ATTR)
  if (lockedNow) {
    element.removeAttribute(LAYER_LOCKED_ATTR)
    success.value = 'قفل لایه برداشته شد.'
  } else {
    element.setAttribute(LAYER_LOCKED_ATTR, '1')
    success.value = 'لایه قفل شد.'
  }
  markVisualStructureDirty()
  syncLayerMetaFromElement(key, element)
}

function escapeCssIdent(value) {
  return String(value || '').replace(/[^a-zA-Z0-9\-_]/g, (char) => `\\${char}`)
}

function resolveManagedImageProxyUrl(rawUrl) {
  const value = String(rawUrl || '').trim()
  if (!value || value.startsWith('data:') || value.startsWith('blob:')) return value
  if (value.startsWith('//')) return `/api/method/mysite.api.management_image_proxy?url=${encodeURIComponent(`https:${value}`)}`
  if (/^https?:\/\//i.test(value)) return `/api/method/mysite.api.management_image_proxy?url=${encodeURIComponent(value)}`
  return value
}

function rewriteExternalImagesInDocument(doc) {
  if (!doc) return
  for (const image of Array.from(doc.querySelectorAll('img'))) {
    const originalSrc = String(image.getAttribute('src') || image.getAttribute('data-src') || '').trim()
    if (!originalSrc) continue
    const nextSrc = resolveManagedImageProxyUrl(originalSrc)
    if (nextSrc && nextSrc !== originalSrc) image.setAttribute('src', nextSrc)
  }
}

function isVisualEditableElement(node) {
  if (!node || node.nodeType !== 1) return false
  const id = String(node.id || '').trim()
  if (id.startsWith('mysite-ve-')) return false
  if (node.closest?.('#mysite-ve-resize-overlay, #mysite-ve-guide-overlay, #mysite-ve-measure-overlay, #mysite-ve-redline-overlay, #mysite-ve-marquee, #mysite-ve-grid-overlay, #mysite-ve-layout-grid-overlay, #mysite-ve-layout-guides-layer, #mysite-ve-rulers, #mysite-ve-text-toolbar')) return false
  const tag = String(node.tagName || '').toLowerCase()
  if (!tag) return false
  if (['script', 'style', 'meta', 'link', 'noscript'].includes(tag)) return false
  return true
}

function ensureVisualNodeId(element) {
  const current = String(element.getAttribute(VISUAL_NODE_ATTR) || '').trim()
  if (current) return current
  const generated = `node-${Math.random().toString(36).slice(2, 10)}`
  element.setAttribute(VISUAL_NODE_ATTR, generated)
  return generated
}

function nthOfTypeIndex(element) {
  if (!element || !element.parentElement) return 1
  const tag = element.tagName
  let idx = 1
  let node = element
  while (node.previousElementSibling) {
    node = node.previousElementSibling
    if (node.tagName === tag) idx += 1
  }
  return idx
}

function buildCssSelector(element) {
  if (!element || !element.ownerDocument) return ''
  const doc = element.ownerDocument
  if (element.id) return `#${escapeCssIdent(element.id)}`
  const tag = String(element.tagName || '').toLowerCase()
  const classTokens = Array.from(element.classList || []).filter(Boolean).slice(0, 3)
  for (const token of classTokens) {
    const candidate = `${tag}.${escapeCssIdent(token)}`
    try {
      if (doc.querySelectorAll(candidate).length === 1) return candidate
    } catch {
      // ignore invalid selectors from malformed class names
    }
  }
  const parts = []
  let node = element
  let depth = 0
  while (node && node.nodeType === 1 && node.tagName.toLowerCase() !== 'html' && depth <= 6) {
    const nodeTag = String(node.tagName || '').toLowerCase()
    if (node.id) {
      parts.unshift(`#${escapeCssIdent(node.id)}`)
      break
    }
    parts.unshift(`${nodeTag}:nth-of-type(${nthOfTypeIndex(node)})`)
    if (nodeTag === 'body') break
    node = node.parentElement
    depth += 1
  }
  return parts.join(' > ')
}

function hasLayerFlagAttr(element, attrName) {
  if (!element || !attrName) return false
  const value = String(element.getAttribute(attrName) || '').trim().toLowerCase()
  return value === '1' || value === 'true' || value === 'yes'
}

function isLayerLockedElement(element) {
  if (!element || !element.closest) return false
  const lockedNode = element.closest(`[${LAYER_LOCKED_ATTR}]`)
  return hasLayerFlagAttr(lockedNode, LAYER_LOCKED_ATTR)
}

function resolveLayerNodeType(element, childCount = 0) {
  const tag = String(element?.tagName || '').toLowerCase()
  if (!tag) return 'node'
  if (String(element?.getAttribute?.(COMPONENT_INSTANCE_ATTR) || '').trim()) return 'instance'
  if (String(element?.getAttribute?.(COMPONENT_MASTER_ATTR) || '').trim()) return 'component'
  if (['img', 'svg', 'picture', 'canvas', 'video'].includes(tag)) return 'image'
  if (['p', 'span', 'a', 'button', 'label', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'small', 'strong', 'em', 'li'].includes(tag)) return 'text'
  if (['input', 'textarea', 'select'].includes(tag)) return 'input'
  if (childCount > 0 || ['div', 'section', 'article', 'main', 'header', 'footer', 'nav', 'aside', 'form', 'ul', 'ol'].includes(tag)) return 'frame'
  return 'node'
}

function isAutoLayoutParentElement(element) {
  if (!element || element.nodeType !== 1) return false
  const inlineDisplay = String(element.style?.display || '').trim().toLowerCase()
  if (inlineDisplay === 'flex' || inlineDisplay === 'inline-flex' || inlineDisplay === 'grid' || inlineDisplay === 'inline-grid') return true
  try {
    const doc = element.ownerDocument
    const win = doc?.defaultView
    const computedDisplay = String(win?.getComputedStyle?.(element)?.display || '').trim().toLowerCase()
    return computedDisplay === 'flex' || computedDisplay === 'inline-flex' || computedDisplay === 'grid' || computedDisplay === 'inline-grid'
  } catch {
    return false
  }
}

function buildLayerMetaForElement(element, childCount = 0) {
  if (!element || element.nodeType !== 1) {
    return {
      hidden: false,
      locked: false,
      node_type: 'node',
      is_component_instance: false,
      is_component_variant: false,
      is_auto_layout_child: false,
    }
  }
  const componentInstance = String(element.getAttribute(COMPONENT_INSTANCE_ATTR) || '').trim()
  const componentVariant = String(element.getAttribute(COMPONENT_VARIANT_ATTR) || 'default').trim() || 'default'
  const hidden = hasLayerFlagAttr(element, LAYER_HIDDEN_ATTR) ||
    String(element.style?.display || '').trim().toLowerCase() === 'none' ||
    String(element.style?.visibility || '').trim().toLowerCase() === 'hidden'
  const locked = hasLayerFlagAttr(element, LAYER_LOCKED_ATTR)
  return {
    hidden,
    locked,
    node_type: resolveLayerNodeType(element, childCount),
    is_component_instance: Boolean(componentInstance),
    is_component_variant: Boolean(componentInstance && componentVariant && componentVariant !== 'default'),
    is_auto_layout_child: isAutoLayoutParentElement(element.parentElement),
  }
}

function nodeLabel(element) {
  const customLabel = String(element?.getAttribute?.(LAYER_LABEL_ATTR) || '').trim()
  if (customLabel) return customLabel
  const tag = String(element?.tagName || '').toLowerCase()
  const id = String(element?.id || '').trim()
  const cls = String(element?.className || '').split(/\s+/).filter(Boolean).slice(0, 2).join('.')
  if (id) return `${tag}#${id}`
  if (cls) return `${tag}.${cls}`
  return `${tag}`
}

function getElementPreviewText(element, limit = 120) {
  if (!element || element.nodeType !== 1) return ''
  let text = ''
  for (const node of Array.from(element.childNodes || [])) {
    if (node?.nodeType !== Node.TEXT_NODE) continue
    const value = String(node.textContent || '').replace(/\s+/g, ' ').trim()
    if (!value) continue
    text = value
    break
  }
  if (!text) {
    text = String(element.getAttribute?.('aria-label') || '').trim() ||
      String(element.getAttribute?.('alt') || '').trim() ||
      String(element.getAttribute?.('title') || '').trim()
  }
  if (!text) return ''
  return text.slice(0, Math.max(1, Number(limit || 120)))
}

function injectVisualEditorStyles(doc) {
  if (!doc) return
  // ensure head exists
  if (!doc.head) {
    const head = doc.createElement('head')
    doc.documentElement?.prepend(head)
  }
  if (!doc.head) return
  const styleId = 'mysite-visual-editor-style'
  if (doc.getElementById(styleId)) return
  const style = doc.createElement('style')
  style.id = styleId
  style.textContent = `
    html, body { caret-color: transparent !important; }
    * { cursor: default !important; }
    a, button, [role=button], [onclick], label { cursor: pointer !important; }
    .mysite-visual-selected {
      outline: 2px solid #18a0fb !important;
      outline-offset: 2px !important;
      box-shadow: 0 0 0 4px rgba(24,160,251,0.15) !important;
      transition: outline-color .14s ease, box-shadow .14s ease;
    }
    .mysite-visual-selected-secondary {
      outline: 2px solid rgba(24,160,251,0.55) !important;
      outline-offset: 1px !important;
      box-shadow: 0 0 0 2px rgba(24,160,251,0.12) !important;
    }
    .mysite-ve-group {
      border: 1px dashed rgba(24,160,251,0.52) !important;
      border-radius: 8px !important;
      padding: 6px !important;
      min-height: 18px;
    }
    #mysite-ve-resize-overlay {
      position: absolute;
      z-index: 2147483000;
      border: 1px solid rgba(24,160,251,0.95);
      box-shadow: 0 0 0 2px rgba(24,160,251,0.16);
      pointer-events: none;
      box-sizing: border-box;
    }
    .mysite-ve-resize-handle {
      position: absolute;
      width: 9px;
      height: 9px;
      border-radius: 50%;
      border: 1px solid #ffffff;
      background: #18a0fb;
      pointer-events: auto;
      padding: 0;
    }
    .mysite-ve-resize-handle-nw { left: -5px; top: -5px; cursor: nwse-resize !important; }
    .mysite-ve-resize-handle-n { left: calc(50% - 4px); top: -5px; cursor: ns-resize !important; }
    .mysite-ve-resize-handle-ne { right: -5px; top: -5px; cursor: nesw-resize !important; }
    .mysite-ve-resize-handle-e { right: -5px; top: calc(50% - 4px); cursor: ew-resize !important; }
    .mysite-ve-resize-handle-se { right: -5px; bottom: -5px; cursor: nwse-resize !important; }
    .mysite-ve-resize-handle-s { left: calc(50% - 4px); bottom: -5px; cursor: ns-resize !important; }
    .mysite-ve-resize-handle-sw { left: -5px; bottom: -5px; cursor: nesw-resize !important; }
    .mysite-ve-resize-handle-w { left: -5px; top: calc(50% - 4px); cursor: ew-resize !important; }
    .mysite-ve-resize-rotate-line {
      position: absolute;
      width: 1px;
      height: 16px;
      left: calc(50% - 0.5px);
      top: -20px;
      background: rgba(24, 160, 251, 0.85);
      pointer-events: none;
    }
    .mysite-ve-resize-handle-rotate {
      left: calc(50% - 5px);
      top: -31px;
      width: 11px;
      height: 11px;
      border-radius: 50%;
      cursor: grab !important;
      background: #ffffff;
      border: 1px solid #18a0fb;
      box-shadow: 0 0 0 2px rgba(24, 160, 251, 0.22);
    }
    #mysite-ve-grid-overlay,
    #mysite-ve-layout-grid-overlay,
    #mysite-ve-layout-guides-layer,
    #mysite-ve-rulers {
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 2147482970;
    }
    #mysite-ve-grid-overlay,
    #mysite-ve-layout-grid-overlay {
      display: none;
    }
    #mysite-ve-rulers {
      z-index: 2147483020;
      display: none;
    }
    .mysite-ve-ruler-top,
    .mysite-ve-ruler-left {
      position: absolute;
      background: rgba(16, 20, 28, 0.92);
      border: 1px solid rgba(120, 136, 160, 0.4);
      color: rgba(200, 214, 233, 0.75);
      font: 10px/1.2 ui-monospace, SFMono-Regular, Menlo, monospace;
      pointer-events: auto;
      user-select: none;
    }
    .mysite-ve-ruler-top {
      height: 18px;
      left: 18px;
      right: 0;
      top: 0;
      border-right: none;
      border-top: none;
      background-image: repeating-linear-gradient(to right, rgba(214, 228, 251, 0.28) 0, rgba(214, 228, 251, 0.28) 1px, transparent 1px, transparent 10px);
      background-size: 40px 100%;
    }
    .mysite-ve-ruler-left {
      width: 18px;
      top: 18px;
      bottom: 0;
      left: 0;
      border-left: none;
      border-bottom: none;
      background-image: repeating-linear-gradient(to bottom, rgba(214, 228, 251, 0.28) 0, rgba(214, 228, 251, 0.28) 1px, transparent 1px, transparent 10px);
      background-size: 100% 40px;
    }
    .mysite-ve-guide-persistent {
      position: absolute;
      pointer-events: auto;
      z-index: 2147483010;
      background: rgba(13, 153, 255, 0.85);
      box-shadow: 0 0 0 1px rgba(13, 153, 255, 0.22);
    }
    .mysite-ve-guide-persistent-v {
      top: 0;
      bottom: 0;
      width: 1px;
      cursor: ew-resize !important;
    }
    .mysite-ve-guide-persistent-h {
      left: 0;
      right: 0;
      height: 1px;
      cursor: ns-resize !important;
    }
    #mysite-ve-text-toolbar {
      position: absolute;
      z-index: 2147483050;
      display: none;
      align-items: center;
      gap: 4px;
      background: rgba(18, 23, 32, 0.95);
      border: 1px solid rgba(105, 124, 151, 0.48);
      box-shadow: 0 12px 28px rgba(0, 0, 0, 0.4);
      border-radius: 9px;
      padding: 5px;
      pointer-events: auto;
    }
    #mysite-ve-text-toolbar button {
      width: 24px;
      height: 24px;
      border-radius: 6px;
      border: 1px solid transparent;
      background: transparent;
      color: #e4edfa;
      font: 600 12px/1 system-ui, -apple-system, sans-serif;
      cursor: pointer;
    }
    #mysite-ve-text-toolbar button:hover {
      background: rgba(255, 255, 255, 0.08);
      border-color: rgba(144, 167, 198, 0.34);
    }
    #mysite-ve-text-toolbar .mysite-ve-text-input {
      width: 62px;
      height: 24px;
      border-radius: 6px;
      border: 1px solid rgba(116, 133, 158, 0.48);
      background: #111827;
      color: #ecf5ff;
      font: 500 11px/1 ui-monospace, SFMono-Regular, Menlo, monospace;
      padding: 0 5px;
    }
    #mysite-ve-guide-overlay {
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 2147482990;
    }
    .mysite-ve-guide-line-v,
    .mysite-ve-guide-line-h {
      position: absolute;
      background: rgba(13, 153, 255, 0.9);
      box-shadow: 0 0 0 1px rgba(13, 153, 255, 0.2);
      display: none;
    }
    .mysite-ve-guide-line-v { width: 1px; top: 0; bottom: 0; }
    .mysite-ve-guide-line-h { height: 1px; left: 0; right: 0; }
    .mysite-ve-guide-label {
      position: absolute;
      display: none;
      border-radius: 999px;
      border: 1px solid rgba(13, 153, 255, 0.55);
      background: rgba(8, 14, 23, 0.92);
      color: #cde8ff;
      font: 600 10px/1 ui-monospace, SFMono-Regular, Menlo, monospace;
      padding: 3px 7px;
      white-space: nowrap;
      pointer-events: none;
      z-index: 2147482996;
    }
    #mysite-ve-measure-overlay {
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 2147483030;
      display: none;
    }
    .mysite-ve-measure-line-x,
    .mysite-ve-measure-line-y {
      position: absolute;
      background: rgba(255, 78, 129, 0.95);
      box-shadow: 0 0 0 1px rgba(255, 78, 129, 0.22);
    }
    .mysite-ve-measure-line-x { height: 1px; }
    .mysite-ve-measure-line-y { width: 1px; }
    .mysite-ve-measure-label {
      position: absolute;
      background: rgba(255, 78, 129, 0.95);
      color: #ffffff;
      border-radius: 999px;
      font: 600 10px/1 ui-monospace, SFMono-Regular, Menlo, monospace;
      padding: 3px 7px;
      transform: translate(-50%, -50%);
      white-space: nowrap;
    }
    #mysite-ve-redline-overlay {
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 2147483040;
      display: none;
    }
    .mysite-ve-redline-line-x,
    .mysite-ve-redline-line-y {
      position: absolute;
      background: rgba(255, 42, 109, 0.95);
      box-shadow: 0 0 0 1px rgba(255, 42, 109, 0.24);
    }
    .mysite-ve-redline-line-x { height: 1px; }
    .mysite-ve-redline-line-y { width: 1px; }
    .mysite-ve-redline-label {
      position: absolute;
      background: rgba(255, 42, 109, 0.95);
      color: #fff;
      border-radius: 999px;
      font: 600 10px/1 ui-monospace, SFMono-Regular, Menlo, monospace;
      padding: 3px 6px;
      transform: translate(-50%, -50%);
      white-space: nowrap;
    }
    [data-mysite-prototype-frame] {
      box-shadow: inset 0 0 0 1px rgba(128, 158, 255, 0.28);
    }
    .mysite-ve-proto-source {
      outline: 2px dashed rgba(244, 114, 182, 0.72) !important;
      outline-offset: 3px !important;
    }
    .mysite-ve-proto-target {
      outline: 2px solid rgba(16, 185, 129, 0.92) !important;
      outline-offset: 3px !important;
      box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.18) !important;
    }
    #mysite-ve-marquee {
      position: absolute;
      pointer-events: none;
      border: 1px solid rgba(13, 153, 255, 0.92);
      background: rgba(13, 153, 255, 0.12);
      box-shadow: inset 0 0 0 1px rgba(13, 153, 255, 0.2);
      display: none;
      z-index: 2147482980;
    }
    #mysite-ve-flow-insertion-line {
      position: absolute;
      height: 2px;
      border-radius: 999px;
      background: #18a0fb;
      box-shadow: 0 0 0 2px rgba(24, 160, 251, 0.2);
      pointer-events: none;
      display: none;
      z-index: 2147482998;
    }
  `
  doc.head.appendChild(style)
}

function applyRawCssToDocument(doc) {
  if (!doc || !doc.head) return
  const styleId = 'mysite-visual-editor-raw-css'
  let style = doc.getElementById(styleId)
  if (!style) {
    style = doc.createElement('style')
    style.id = styleId
    doc.head.appendChild(style)
  }
  style.textContent = String(rawCss.value || '')
}

function applyVisualLayerTreeState(rows, index, childrenMap) {
  const previousExpanded = visualExpandedMap.value || {}
  const nextExpanded = {}
  for (const row of rows || []) {
    if (Number(row?.child_count || 0) <= 0) continue
    const rowId = String(row.id || '')
    if (!rowId) continue
    nextExpanded[rowId] = Object.prototype.hasOwnProperty.call(previousExpanded, rowId) ? Boolean(previousExpanded[rowId]) : true
  }

  visualLayers.value = rows || []
  visualLayerIndex.value = index || {}
  visualChildrenMap.value = childrenMap || {}
  visualExpandedMap.value = nextExpanded
  triggerRef(visualLayers)
  triggerRef(visualLayerIndex)
  triggerRef(visualChildrenMap)
  triggerRef(visualExpandedMap)
}

async function buildVisualLayerTreeWorkerAsync(doc, options = {}) {
  if (!doc?.body) return null
  const worker = getLayerScanWorker()
  if (!worker) return null
  const html = String(doc.body.innerHTML || '')
  if (!html || html.length < LAYER_SCAN_WORKER_MIN_HTML_LEN) return null

  const { loadToken = null, scanToken = null } = options || {}
  const requestId = ++layerScanWorkerRequestId
  const payload = {
    requestId,
    html,
    maxNodes: MAX_VISUAL_LAYER_NODES,
    maxDepth: MAX_VISUAL_LAYER_DEPTH,
    maxChildren: MAX_VISUAL_CHILDREN_PER_NODE,
    maxMs: Math.max(600, MAX_VISUAL_LAYER_SCAN_MS),
  }

  const response = await new Promise((resolve, reject) => {
    let timeoutHandle = null
    const onMessage = (event) => {
      const data = event?.data || {}
      if (Number(data.requestId || 0) !== requestId) return
      cleanup()
      resolve(data)
    }
    const onError = (error) => {
      cleanup()
      reject(error)
    }
    const cleanup = () => {
      if (timeoutHandle !== null) window.clearTimeout(timeoutHandle)
      worker.removeEventListener('message', onMessage)
      worker.removeEventListener('error', onError)
    }
    timeoutHandle = window.setTimeout(() => {
      cleanup()
      reject(new Error('layer-worker-timeout'))
    }, LAYER_SCAN_WORKER_TIMEOUT_MS)
    worker.addEventListener('message', onMessage)
    worker.addEventListener('error', onError)
    worker.postMessage(payload)
  })

  if (!response?.ok) {
    const message = String(response?.error || 'layer-worker-failed')
    throw new Error(message)
  }
  if ((loadToken !== null && loadToken !== previewFrameLoadToken) || (scanToken !== null && scanToken !== visualLayerScanToken)) {
    return { timed_out: false, truncated: false, cancelled: true, from_worker: true }
  }

  const rows = []
  const index = {}
  const childrenMap = {}
  const tmpToRealId = {}

  const registerChild = (parentId, childId) => {
    const key = parentId ? String(parentId) : '__root__'
    if (!Array.isArray(childrenMap[key])) childrenMap[key] = []
    childrenMap[key].push(childId)
  }

  const workerRows = Array.isArray(response.rows) ? response.rows : []
  for (const workerRow of workerRows) {
    if ((loadToken !== null && loadToken !== previewFrameLoadToken) || (scanToken !== null && scanToken !== visualLayerScanToken)) {
      return { timed_out: false, truncated: false, cancelled: true, from_worker: true }
    }
    const path = String(workerRow?.path || '').trim()
    const element = resolveElementByTreePath(doc, path)
    if (!isVisualEditableElement(element)) continue
    const realId = ensureVisualNodeId(element)
    if (!realId) continue
    const parentTmp = String(workerRow?.parent_tmp_id || '').trim()
    const parentId = parentTmp ? String(tmpToRealId[parentTmp] || '') : ''
    const row = {
      id: realId,
      depth: Math.max(0, Number.parseInt(String(workerRow?.depth || '0'), 10) || 0),
      parent_id: parentId,
      tag: String(workerRow?.tag || element.tagName || '').toLowerCase(),
      label: nodeLabel(element),
      selector: '',
      original_text: String(workerRow?.original_text || getElementPreviewText(element, 300)),
      child_count: Math.max(0, Number.parseInt(String(workerRow?.child_count || '0'), 10) || 0),
      ...buildLayerMetaForElement(element, Math.max(0, Number.parseInt(String(workerRow?.child_count || '0'), 10) || 0)),
    }
    rows.push(row)
    index[realId] = row
    registerChild(parentId, realId)
    const tmpId = String(workerRow?.tmp_id || '').trim()
    if (tmpId) tmpToRealId[tmpId] = realId
  }

  applyVisualLayerTreeState(rows, index, childrenMap)
  return {
    timed_out: Boolean(response.timed_out),
    truncated: Boolean(response.truncated || rows.length >= MAX_VISUAL_LAYER_NODES),
    cancelled: false,
    from_worker: true,
  }
}

async function buildVisualLayerTreeFallbackAsync(doc, options = {}) {
  if (!doc?.body) { return { timed_out: false, truncated: false, cancelled: false } }
  const { loadToken = null, scanToken = null } = options || {}
  const rows = [], index = {}, childrenMap = {}

  function registerChild(parentId, childId) {
    const key = parentId ? String(parentId) : '__root__'
    if (!Array.isArray(childrenMap[key])) childrenMap[key] = []
    childrenMap[key].push(childId)
  }

  function editableChildrenFor(element) {
    const result = []
    for (const child of (element?.children || [])) {
      if (!isVisualEditableElement(child)) continue
      result.push(child)
      if (result.length >= MAX_VISUAL_CHILDREN_PER_NODE) break
    }
    return result
  }

  const queue = []
  for (const child of Array.from(doc.body.children || [])) queue.push({ element: child, depth: 0, parentId: '' })

  let cursor = 0
  const scanStartedAt = performance.now()
  let timedOut = false, cancelled = false

  while (cursor < queue.length && rows.length < MAX_VISUAL_LAYER_NODES) {
    if ((loadToken !== null && loadToken !== previewFrameLoadToken) || (scanToken !== null && scanToken !== visualLayerScanToken)) {
      cancelled = true; break
    }
    if (performance.now() - scanStartedAt >= MAX_VISUAL_LAYER_SCAN_MS) {
      timedOut = true; break
    }
    const startedAt = performance.now()
    while (cursor < queue.length && rows.length < MAX_VISUAL_LAYER_NODES) {
      const current = queue[cursor++]
      const element = current?.element
      const depth = Number(current?.depth || 0)
      const parentId = String(current?.parentId || '')
      if (!isVisualEditableElement(element) || depth > MAX_VISUAL_LAYER_DEPTH) continue

      const id = ensureVisualNodeId(element)
      const editableChildren = editableChildrenFor(element)
      const layer = {
        id, depth, parent_id: parentId, tag: String(element.tagName || '').toLowerCase(),
        label: nodeLabel(element), selector: '', original_text: getElementPreviewText(element, 300),
        child_count: editableChildren.length,
        ...buildLayerMetaForElement(element, editableChildren.length),
      }
      rows.push(layer)
      index[id] = layer
      registerChild(parentId, id)
      for (const child of editableChildren) queue.push({ element: child, depth: depth + 1, parentId: id })
      if (performance.now() - startedAt >= LAYER_SCAN_CHUNK_MS) break
    }
    if (cursor < queue.length && rows.length < MAX_VISUAL_LAYER_NODES) {
      await new Promise((resolve) => window.setTimeout(resolve, 0))
    }
  }

  if (cancelled) return { timed_out: false, truncated: false, cancelled: true }
  applyVisualLayerTreeState(rows, index, childrenMap)
  return { timed_out: timedOut, truncated: rows.length >= MAX_VISUAL_LAYER_NODES || timedOut, cancelled }
}

async function runVisualLayerScan(doc, options = {}) {
  if (!doc?.body) return
  const loadToken = Number(options?.loadToken ?? previewFrameLoadToken)
  const focusNodeId = String(options?.focusNodeId || '').trim()
  const scanToken = ++visualLayerScanToken
  layerScanInProgress.value = true
  try {
    let scanState = null
    try {
      scanState = await buildVisualLayerTreeWorkerAsync(doc, { loadToken, scanToken })
    } catch {
      scanState = null
    }
    if (!scanState) {
      scanState = await buildVisualLayerTreeFallbackAsync(doc, { loadToken, scanToken })
    }
    if (!scanState || scanState.cancelled) return
    if (loadToken !== previewFrameLoadToken || scanToken !== visualLayerScanToken) return
    applyPrototypeModelToDocument(doc)
    if (focusNodeId) selectVisualLayer(focusNodeId)
    if (scanState?.timed_out) success.value = 'فقط بخشی از لایه‌ها بارگذاری شد (حد زمانی).'
    else success.value = scanState?.from_worker ? 'اسکن لایه‌ها با worker انجام شد.' : 'اسکن لایه‌ها انجام شد.'
  } catch (err) {
    if (loadToken !== previewFrameLoadToken || scanToken !== visualLayerScanToken) return
    error.value = err?.message || 'خطا در اسکن لایه‌ها.'
  } finally {
    if (scanToken === visualLayerScanToken) layerScanInProgress.value = false
  }
}

async function scanPreviewLayers() {
  if (!visualFrameDocument || !previewInitialized.value) return
  error.value = ''
  success.value = ''
  await runVisualLayerScan(visualFrameDocument, { loadToken: previewFrameLoadToken })
}

function ensureLayerSelector(nodeId, element = null) {
  const key = String(nodeId || '').trim()
  if (!key) return ''
  const current = visualLayerIndex.value?.[key]
  if (!current) return ''
  const existingSelector = String(current.selector || '').trim()
  if (existingSelector) return existingSelector
  const targetElement = isVisualEditableElement(element) ? element : getVisualElementById(key)
  if (!targetElement) return ''
  const computedSelector = String(buildCssSelector(targetElement) || '').trim()
  if (!computedSelector) return ''
  // ⚡ Direct mutation on shallowRef object — O(1) instead of spreading whole map + layers array
  current.selector = computedSelector
  triggerRef(visualLayerIndex)
  return computedSelector
}

function getVisualElementById(nodeId) {
  if (!visualFrameDocument || !nodeId) return null
  try { return visualFrameDocument.querySelector(`[${VISUAL_NODE_ATTR}="${cssEscape(nodeId)}"]`) } catch { return null }
}

// ⚡ PERFORMANCE: Read only inline styles synchronously (no layout reflow).
// Then asynchronously read computed styles in background without blocking the UI.
let _computedStyleTimer = null
let _computedStyleIdleHandle = null
function clearComputedStyleTask() {
  if (_computedStyleTimer !== null) {
    window.clearTimeout(_computedStyleTimer)
    _computedStyleTimer = null
  }
  if (_computedStyleIdleHandle !== null && typeof window.cancelIdleCallback === 'function') {
    window.cancelIdleCallback(_computedStyleIdleHandle)
  }
  _computedStyleIdleHandle = null
}
function syncVisualPropsFromElement(element) {
  if (!element) {
    clearComputedStyleTask()
    resetVisualProps()
    return
  }

  const s = element.style
  const inline = (prop) => String(s[prop] || '')
  const inlineParagraphSpacing = String(s.getPropertyValue('--mysite-paragraph-spacing') || '')
  const inlineRotation = splitTransformRotation(String(s.transform || '')).rotateDeg

  // Phase 1: fill from inline styles instantly (zero reflow)
  visualProps.value = {
    text_content: _quickTextOf(element),
    display: inline('display'), flexDirection: inline('flexDirection'),
    justifyContent: inline('justifyContent'), alignItems: inline('alignItems'),
    flexWrap: inline('flexWrap'), flexGrow: inline('flexGrow'), flexShrink: inline('flexShrink'),
    gap: inline('gap'), color: inline('color'), fontFamily: inline('fontFamily'), fontSize: inline('fontSize'),
    fontWeight: inline('fontWeight'), lineHeight: inline('lineHeight'),
    letterSpacing: inline('letterSpacing'), textAlign: inline('textAlign'),
    paragraphSpacing: inlineParagraphSpacing,
    fontFeatureSettings: inline('fontFeatureSettings'), fontVariantLigatures: inline('fontVariantLigatures'),
    textIndent: inline('textIndent'), listStyleType: inline('listStyleType'),
    listStylePosition: inline('listStylePosition'), whiteSpace: inline('whiteSpace'),
    wordSpacing: inline('wordSpacing'), textTransform: inline('textTransform'),
    textDecoration: inline('textDecoration'),
    backgroundColor: inline('backgroundColor'), borderColor: inline('borderColor'),
    borderWidth: inline('borderWidth'), borderRadius: inline('borderRadius'),
    boxShadow: inline('boxShadow'), opacity: inline('opacity'), zIndex: inline('zIndex'),
    width: inline('width'), minWidth: inline('minWidth'), maxWidth: inline('maxWidth'),
    height: inline('height'), minHeight: inline('minHeight'), maxHeight: inline('maxHeight'),
    overflowX: inline('overflowX'), overflowY: inline('overflowY'),
    margin: inline('margin'), padding: inline('padding'),
    transitionDuration: inline('transitionDuration'), position: inline('position'),
    top: inline('top'), right: inline('right'), bottom: inline('bottom'), left: inline('left'),
    rotation: `${inlineRotation}deg`,
  }

  // Phase 2: fill empty fields from computed styles (deferred to avoid layout block)
  clearComputedStyleTask()
  const readComputedStyles = () => {
    _computedStyleIdleHandle = null
    _computedStyleTimer = null
    if (visualSelectedElement !== element) return
    if (!element.isConnected) return   // element may have been removed
    try {
      const iframeWin = visualPreviewFrame.value?.contentWindow
      const cs = iframeWin ? iframeWin.getComputedStyle(element) : null
      if (!cs) return
      const p = (prop) => String(s[prop] || '') || String(cs[prop] || '')
      const rotation = splitTransformRotation(String(s.transform || cs.transform || '')).rotateDeg
      const paragraphSpacing = String(s.getPropertyValue('--mysite-paragraph-spacing') || cs.getPropertyValue('--mysite-paragraph-spacing') || '')
      visualProps.value = {
        ...visualProps.value,
        display: p('display'), flexDirection: p('flexDirection'),
        justifyContent: p('justifyContent'), alignItems: p('alignItems'),
        flexWrap: p('flexWrap'), flexGrow: p('flexGrow'), flexShrink: p('flexShrink'),
        gap: p('gap'), color: p('color'), fontFamily: p('fontFamily'),
        fontSize: p('fontSize'), fontWeight: p('fontWeight'), lineHeight: p('lineHeight'),
        letterSpacing: p('letterSpacing'), textAlign: p('textAlign'),
        paragraphSpacing,
        fontFeatureSettings: p('fontFeatureSettings'), fontVariantLigatures: p('fontVariantLigatures'),
        textIndent: p('textIndent'), listStyleType: p('listStyleType'),
        listStylePosition: p('listStylePosition'), whiteSpace: p('whiteSpace'),
        wordSpacing: p('wordSpacing'), textTransform: p('textTransform'),
        textDecoration: p('textDecoration'),
        backgroundColor: p('backgroundColor'), borderColor: p('borderColor'),
        borderWidth: p('borderWidth'), borderRadius: p('borderRadius'), boxShadow: p('boxShadow'),
        opacity: p('opacity'), zIndex: p('zIndex'), position: p('position'),
        width: p('width'), minWidth: p('minWidth'), maxWidth: p('maxWidth'),
        height: p('height'), minHeight: p('minHeight'), maxHeight: p('maxHeight'),
        overflowX: p('overflowX'), overflowY: p('overflowY'),
        margin: p('margin'), padding: p('padding'), transitionDuration: p('transitionDuration'),
        top: p('top'), right: p('right'), bottom: p('bottom'), left: p('left'),
        rotation: `${rotation}deg`,
      }
    } catch { /* cross-origin or element removed */ }
  }
  if (typeof window.requestIdleCallback === 'function') {
    _computedStyleIdleHandle = window.requestIdleCallback(readComputedStyles, { timeout: COMPUTED_STYLE_IDLE_TIMEOUT_MS })
  } else {
    _computedStyleTimer = window.setTimeout(readComputedStyles, COMPUTED_STYLE_FALLBACK_DELAY_MS)
  }
}

function resolveSelectionRangeIds(anchorId, targetId, explicitIds = null) {
  if (Array.isArray(explicitIds) && explicitIds.length) {
    return explicitIds.map((row) => String(row || '').trim()).filter(Boolean)
  }
  const startId = String(anchorId || '').trim()
  const endId = String(targetId || '').trim()
  if (!startId || !endId) return []
  const rows = Array.isArray(filteredVisualLayers.value) && filteredVisualLayers.value.length
    ? filteredVisualLayers.value
    : (Array.isArray(visualLayers.value) ? visualLayers.value : [])
  const ids = rows.map((row) => String(row?.id || '')).filter(Boolean)
  const startIndex = ids.indexOf(startId)
  const endIndex = ids.indexOf(endId)
  if (startIndex < 0 || endIndex < 0) return [endId]
  const from = Math.min(startIndex, endIndex)
  const to = Math.max(startIndex, endIndex)
  return ids.slice(from, to + 1)
}

function selectVisualLayer(nodeId, options = {}) {
  const targetId = String(nodeId || '').trim()
  if (!targetId) return
  const element = getVisualElementById(targetId)
  if (!element) return

  const range = Boolean(options?.range)
  const additive = Boolean(options?.additive)
  const toggle = Boolean(options?.toggle)
  let nextIds = Array.isArray(visualSelectedIds.value) ? [...visualSelectedIds.value] : []

  if (range) {
    const anchorId = String(visualSelectedId.value || nextIds[0] || targetId).trim() || targetId
    const rangeIds = resolveSelectionRangeIds(anchorId, targetId, options?.rangeIds)
    if (!rangeIds.length) {
      nextIds = [targetId]
    } else if (additive) {
      const set = new Set(nextIds)
      for (const id of rangeIds) set.add(id)
      nextIds = Array.from(set)
    } else {
      nextIds = [...rangeIds]
    }
  } else if (!additive) {
    nextIds = [targetId]
  } else {
    const exists = nextIds.includes(targetId)
    if (exists && toggle) {
      nextIds = nextIds.filter((row) => row !== targetId)
    } else if (!exists) {
      nextIds.push(targetId)
    }
  }

  if (!nextIds.length) {
    clearVisualSelection()
    return
  }

  let primaryId = String(visualSelectedId.value || '').trim()
  if (range) {
    primaryId = targetId
  } else if (!additive) {
    primaryId = targetId
  } else if (toggle && nextIds.includes(targetId)) {
    primaryId = targetId
  } else if (!primaryId || !nextIds.includes(primaryId)) {
    primaryId = nextIds[nextIds.length - 1]
  }
  visualSelectedIds.value = nextIds
  visualSelectedId.value = primaryId
  visualSelectedElement = getVisualElementById(primaryId)

  applySelectionClasses()

  const primaryElement = visualSelectedElement
  if (!primaryElement) {
    resetVisualProps()
    rawHtmlInput.value = ''
    return
  }

  rawHtmlInput.value = String(primaryElement.innerHTML || '')
  ensureLayerSelector(primaryId, primaryElement)

  const currentLayer = visualLayerIndex.value?.[primaryId]
  if (currentLayer) {
    const quickText = _quickTextOf(primaryElement)
    if (quickText !== String(currentLayer.original_text || '')) {
      currentLayer.original_text = quickText
      triggerRef(visualLayerIndex)
    }
  }

  if (String(visualLayerQuery.value || '').trim()) {
    const visibleIds = new Set((filteredVisualLayers.value || []).map((row) => String(row?.id || '')))
    if (!visibleIds.has(primaryId)) visualLayerQuery.value = ''
  }

  expandLayerAncestors(primaryId)
  nextTick(() => focusLayerRow(primaryId))
  syncVisualPropsFromElement(primaryElement)
  syncPrototypeDraftFromSelection()
  syncRedlineOverlay()
  nextTick(() => { syncResizeOverlay(); syncRedlineOverlay() })
}

// ⚡ Fast text extraction — avoids innerText reflow
function _quickTextOf(element) {
  for (const node of element.childNodes) {
    if (node.nodeType === 3) {   // TEXT_NODE
      const v = node.nodeValue.replace(/\s+/g, ' ').trim()
      if (v) return v.slice(0, 120)
    }
  }
  return (
    element.getAttribute('aria-label') ||
    element.getAttribute('alt') ||
    element.getAttribute('title') ||
    element.getAttribute('placeholder') ||
    ''
  ).slice(0, 120)
}

function applyVisualOverridesToDocument(doc) {
  const rows = Object.values(visualOverridesMap.value || {})
  if (!rows.length || !doc) return
  for (const row of rows) {
    const selector = String(row?.selector || '').trim()
    if (!selector) continue
    let elements = []
    try { elements = Array.from(doc.querySelectorAll(selector)) } catch { elements = [] }
    for (const element of elements) {
      if (row.apply_html) element.innerHTML = String(row.html_content ?? '')
      else if (row.apply_text) element.textContent = String(row.text_content ?? '')
      for (const [key, value] of Object.entries(row.styles || {})) {
        if (!value) continue
        const styleKey = String(key || '').trim()
        if (!styleKey) continue
        if (styleKey.startsWith('--') || styleKey.includes('-')) {
          element.style.setProperty(styleKey, String(value))
        } else {
          element.style[styleKey] = String(value)
        }
      }
    }
  }
}

function findPrototypeFrameForElement(element) {
  if (!element || !prototypeModel.value?.frames) return null
  for (const frame of Object.values(prototypeModel.value.frames || {})) {
    const selector = String(frame?.selector || '').trim()
    if (!selector) continue
    try {
      const matched = element.closest(selector)
      if (matched) return frame
    } catch {
      // ignore invalid selector
    }
  }
  return null
}

function getSelectedPrototypeFrame() {
  if (!visualSelectedElement) return null
  return findPrototypeFrameForElement(visualSelectedElement)
}

function getPrototypeLinkForFrame(frameId) {
  const sourceId = normalizePrototypeFrameId(frameId)
  if (!sourceId) return null
  const links = Array.isArray(prototypeModel.value?.links) ? prototypeModel.value.links : []
  return links.find((row) => String(row?.source_frame_id || '') === sourceId) || null
}

function syncPrototypeDraftFromSelection() {
  const selectedFrame = getSelectedPrototypeFrame()
  prototypeFrameIdDraft.value = String(selectedFrame?.id || '').trim()
  const selectedLink = getPrototypeLinkForFrame(selectedFrame?.id)
  prototypeLinkTargetFrameId.value = String(selectedLink?.target_frame_id || '').trim()
  prototypeLinkTransition.value = String(selectedLink?.transition || 'instant').trim() || 'instant'
  prototypeLinkDurationMs.value = Math.min(8000, Math.max(60, Number.parseInt(String(selectedLink?.duration_ms || 280), 10) || 280))
  prototypeLinkSmartAnimate.value = Boolean(selectedLink?.smart_animate || prototypeLinkTransition.value === 'smart-animate')
}

function onPrototypeFrameIdDraftInput(value) {
  prototypeFrameIdDraft.value = normalizePrototypeFrameId(value)
}

function onPrototypeLinkTargetFrameIdInput(value) {
  prototypeLinkTargetFrameId.value = normalizePrototypeFrameId(value)
}

function onPrototypeLinkTransitionInput(value) {
  const next = String(value || '').trim().toLowerCase()
  prototypeLinkTransition.value = ['instant', 'dissolve', 'smart-animate'].includes(next) ? next : 'instant'
}

function onPrototypeLinkDurationMsInput(value) {
  prototypeLinkDurationMs.value = Math.min(8000, Math.max(60, Number.parseInt(String(value || 280), 10) || 280))
}

function togglePrototypeLinkSmartAnimate() {
  prototypeLinkSmartAnimate.value = !prototypeLinkSmartAnimate.value
}

function setPrototypeStartFrame(value) {
  const frameId = normalizePrototypeFrameId(value)
  const next = normalizePrototypeModel(prototypeModel.value)
  next.start_frame_id = frameId && next.frames?.[frameId] ? frameId : ''
  prototypeModel.value = next
  applyPrototypeModelToDocument(visualFrameDocument)
}

function setPrototypeFrameForSelection() {
  if (!visualSelectedElement || !visualSelectedId.value) return false
  const selector = ensureLayerSelector(visualSelectedId.value, visualSelectedElement)
  if (!selector) return false
  const frameIdSeed = prototypeFrameIdDraft.value || visualSelectedLayer.value?.label || visualSelectedLayer.value?.id || visualSelectedId.value
  const frameId = normalizePrototypeFrameId(frameIdSeed)
  if (!frameId) return false
  const next = normalizePrototypeModel(prototypeModel.value)
  next.frames[frameId] = {
    id: frameId,
    selector,
    label: String(visualSelectedLayer.value?.label || frameId).trim().slice(0, 140),
  }
  if (!next.start_frame_id || !next.frames[next.start_frame_id]) next.start_frame_id = frameId
  prototypeModel.value = normalizePrototypeModel(next)
  syncPrototypeDraftFromSelection()
  applyPrototypeModelToDocument(visualFrameDocument)
  success.value = 'Prototype frame ثبت شد.'
  error.value = ''
  return true
}

function removePrototypeFrameForSelection() {
  const selectedFrame = getSelectedPrototypeFrame()
  if (!selectedFrame?.id) return false
  const frameId = normalizePrototypeFrameId(selectedFrame.id)
  const next = normalizePrototypeModel(prototypeModel.value)
  delete next.frames[frameId]
  next.links = (next.links || []).filter((row) => String(row?.source_frame_id || '') !== frameId && String(row?.target_frame_id || '') !== frameId)
  if (next.start_frame_id === frameId) next.start_frame_id = Object.keys(next.frames || {})[0] || ''
  prototypeModel.value = normalizePrototypeModel(next)
  syncPrototypeDraftFromSelection()
  applyPrototypeModelToDocument(visualFrameDocument)
  success.value = 'Prototype frame حذف شد.'
  error.value = ''
  return true
}

function setPrototypeLinkForSelection() {
  const selectedFrame = getSelectedPrototypeFrame()
  if (!selectedFrame?.id) return false
  const sourceFrameId = normalizePrototypeFrameId(selectedFrame.id)
  const targetFrameId = normalizePrototypeFrameId(prototypeLinkTargetFrameId.value)
  if (!sourceFrameId || !targetFrameId || sourceFrameId === targetFrameId) return false
  const next = normalizePrototypeModel(prototypeModel.value)
  if (!next.frames[sourceFrameId] || !next.frames[targetFrameId]) return false
  const links = Array.isArray(next.links) ? [...next.links] : []
  const rowIndex = links.findIndex((row) => String(row?.source_frame_id || '') === sourceFrameId)
  const transition = String(prototypeLinkTransition.value || 'instant').trim().toLowerCase()
  const normalizedTransition = ['instant', 'dissolve', 'smart-animate'].includes(transition) ? transition : 'instant'
  const linkRow = {
    id: `link-${sourceFrameId}-${targetFrameId}`,
    source_frame_id: sourceFrameId,
    target_frame_id: targetFrameId,
    trigger: 'click',
    transition: normalizedTransition,
    duration_ms: Math.min(8000, Math.max(60, Number.parseInt(String(prototypeLinkDurationMs.value || 280), 10) || 280)),
    smart_animate: Boolean(prototypeLinkSmartAnimate.value || normalizedTransition === 'smart-animate'),
  }
  if (rowIndex === -1) links.push(linkRow)
  else links[rowIndex] = linkRow
  next.links = links
  prototypeModel.value = normalizePrototypeModel(next)
  applyPrototypeModelToDocument(visualFrameDocument)
  success.value = 'Prototype link ذخیره شد.'
  error.value = ''
  return true
}

function removePrototypeLinkForSelection() {
  const selectedFrame = getSelectedPrototypeFrame()
  if (!selectedFrame?.id) return false
  const sourceFrameId = normalizePrototypeFrameId(selectedFrame.id)
  const next = normalizePrototypeModel(prototypeModel.value)
  const before = Array.isArray(next.links) ? next.links.length : 0
  next.links = (next.links || []).filter((row) => String(row?.source_frame_id || '') !== sourceFrameId)
  if (next.links.length === before) return false
  prototypeModel.value = normalizePrototypeModel(next)
  syncPrototypeDraftFromSelection()
  applyPrototypeModelToDocument(visualFrameDocument)
  success.value = 'Prototype link حذف شد.'
  error.value = ''
  return true
}

function togglePrototypePreview() {
  const next = normalizePrototypeModel(prototypeModel.value)
  next.preview_enabled = !Boolean(next.preview_enabled)
  prototypeModel.value = next
  applyPrototypeModelToDocument(visualFrameDocument)
}

function applyPrototypeModelToDocument(doc) {
  if (!doc?.body) return
  for (const row of Array.from(doc.querySelectorAll('[data-mysite-prototype-frame]'))) {
    row.removeAttribute('data-mysite-prototype-frame')
  }
  const frames = Object.values(prototypeModel.value?.frames || {})
  for (const frame of frames) {
    const selector = String(frame?.selector || '').trim()
    const frameId = String(frame?.id || '').trim()
    if (!selector || !frameId) continue
    let matched = []
    try { matched = Array.from(doc.querySelectorAll(selector)) } catch { matched = [] }
    for (const element of matched) element.setAttribute('data-mysite-prototype-frame', frameId)
  }
}

function focusPrototypeStartFrame(doc) {
  if (!prototypeModel.value?.preview_enabled) return
  const frameId = normalizePrototypeFrameId(prototypeModel.value?.start_frame_id || '')
  if (!frameId) return
  const frame = prototypeModel.value?.frames?.[frameId]
  const selector = String(frame?.selector || '').trim()
  if (!selector) return
  let element = null
  try { element = (doc || visualFrameDocument)?.querySelector(selector) } catch { element = null }
  if (!element) return
  element.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' })
  element.classList.add('mysite-ve-proto-target')
  window.setTimeout(() => element.classList.remove('mysite-ve-proto-target'), 420)
}

function runPrototypeTransition(sourceFrame, targetFrame, link) {
  const doc = visualFrameDocument
  if (!doc) return
  const sourceSelector = String(sourceFrame?.selector || '').trim()
  const targetSelector = String(targetFrame?.selector || '').trim()
  if (!targetSelector) return
  const targetElement = (() => {
    try { return doc.querySelector(targetSelector) } catch { return null }
  })()
  if (!targetElement) return
  const sourceElement = (() => {
    if (!sourceSelector) return null
    try { return doc.querySelector(sourceSelector) } catch { return null }
  })()
  const transition = String(link?.transition || 'instant').trim().toLowerCase()
  const duration = Math.min(8000, Math.max(60, Number.parseInt(String(link?.duration_ms || 280), 10) || 280))
  const smart = Boolean(link?.smart_animate || transition === 'smart-animate')
  targetElement.scrollIntoView({ behavior: transition === 'instant' ? 'auto' : 'smooth', block: 'center', inline: 'nearest' })
  targetElement.classList.add('mysite-ve-proto-target')
  if (sourceElement) sourceElement.classList.add('mysite-ve-proto-source')
  if (transition !== 'instant') {
    const sourceOpacity = sourceElement?.style?.opacity || ''
    const targetOpacity = targetElement.style.opacity || ''
    targetElement.style.transition = `opacity ${duration}ms ease`
    targetElement.style.opacity = '0.2'
    if (sourceElement) {
      sourceElement.style.transition = `opacity ${duration}ms ease`
      sourceElement.style.opacity = smart ? '0.05' : '0.25'
    }
    window.requestAnimationFrame(() => {
      targetElement.style.opacity = targetOpacity || '1'
    })
    window.setTimeout(() => {
      if (sourceElement) {
        sourceElement.style.opacity = sourceOpacity
        sourceElement.style.transition = ''
      }
      targetElement.style.transition = ''
    }, duration + 40)
  }
  window.setTimeout(() => {
    targetElement.classList.remove('mysite-ve-proto-target')
    if (sourceElement) sourceElement.classList.remove('mysite-ve-proto-source')
  }, duration + 280)
}

function tryHandlePrototypePreviewClick(event, targetElement) {
  if (!prototypeModel.value?.preview_enabled) return false
  if (String(activeTool.value || 'select') !== 'select') return false
  if (event?.shiftKey || event?.metaKey || event?.ctrlKey || event?.altKey) return false
  const frame = findPrototypeFrameForElement(targetElement)
  if (!frame?.id) return false
  const link = getPrototypeLinkForFrame(frame.id)
  if (!link) return false
  const targetFrameId = normalizePrototypeFrameId(link.target_frame_id)
  const targetFrame = prototypeModel.value?.frames?.[targetFrameId]
  if (!targetFrame) return false
  event.preventDefault()
  event.stopPropagation()
  runPrototypeTransition(frame, targetFrame, link)
  const next = normalizePrototypeModel(prototypeModel.value)
  next.start_frame_id = targetFrameId
  prototypeModel.value = next
  return true
}

let _clickThrottleTimer = null
function resolveEventTargetElement(target) {
  if (!target) return null
  if (target.nodeType === Node.ELEMENT_NODE) return target
  if (target.nodeType === Node.TEXT_NODE) return target.parentElement
  return null
}

function resolvePointerPointInFrame(event) {
  const frameWindow = visualPreviewFrame.value?.contentWindow
  const scrollX = Number(frameWindow?.scrollX || 0)
  const scrollY = Number(frameWindow?.scrollY || 0)
  const zoom = Math.max(0.01, Number(canvasZoom.value || 1))
  return {
    x: Math.max(0, Math.round((Number(event?.clientX || 0) + scrollX) / zoom)),
    y: Math.max(0, Math.round((Number(event?.clientY || 0) + scrollY) / zoom)),
  }
}

function isInlineTextTarget(element) {
  if (!isVisualEditableElement(element)) return false
  const tag = String(element?.tagName || '').toLowerCase()
  if (!tag) return false
  if (['input', 'textarea', 'select'].includes(tag)) return false
  if (['p', 'span', 'a', 'button', 'label', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'small', 'strong', 'em'].includes(tag)) return true
  if (element.childElementCount > 0) return false
  const quickText = _quickTextOf(element)
  return Boolean(String(quickText || '').trim())
}

function ensureTextToolbar(doc) {
  if (!doc?.body) return null
  let toolbar = doc.getElementById('mysite-ve-text-toolbar')
  if (!toolbar) {
    toolbar = doc.createElement('div')
    toolbar.id = 'mysite-ve-text-toolbar'
    toolbar.innerHTML = [
      '<button type=\"button\" data-cmd=\"bold\" title=\"Bold\">B</button>',
      '<button type=\"button\" data-cmd=\"italic\" title=\"Italic\">I</button>',
      '<button type=\"button\" data-cmd=\"underline\" title=\"Underline\">U</button>',
      '<button type=\"button\" data-cmd=\"align-left\" title=\"Align Left\">L</button>',
      '<button type=\"button\" data-cmd=\"align-center\" title=\"Align Center\">C</button>',
      '<button type=\"button\" data-cmd=\"align-right\" title=\"Align Right\">R</button>',
      '<input class=\"mysite-ve-text-input\" data-cmd=\"font-size\" type=\"number\" min=\"8\" max=\"180\" step=\"1\" value=\"16\" title=\"Font Size\" />',
      '<input class=\"mysite-ve-text-input\" data-cmd=\"color\" type=\"color\" value=\"#111111\" title=\"Color\" />',
      '<button type=\"button\" data-cmd=\"done\" title=\"Done\">✓</button>',
    ].join('')
    doc.body.appendChild(toolbar)

    toolbar.addEventListener('mousedown', (event) => {
      event.preventDefault()
      event.stopPropagation()
    }, true)

    toolbar.addEventListener('click', (event) => {
      const cmd = String(event?.target?.getAttribute?.('data-cmd') || '').trim()
      if (!cmd) return
      event.preventDefault()
      event.stopPropagation()
      if (cmd === 'done') {
        void finishInlineTextEditing(true)
        return
      }
      if (cmd === 'align-left' || cmd === 'align-center' || cmd === 'align-right') {
        const value = cmd.replace('align-', '')
        if (inlineTextEditState?.element) inlineTextEditState.element.style.textAlign = value
      } else if (cmd === 'bold' || cmd === 'italic' || cmd === 'underline') {
        try {
          doc.execCommand(cmd, false)
        } catch {
          // noop
        }
      }
      inlineTextEditState?.element?.focus?.()
    }, true)

    toolbar.addEventListener('input', (event) => {
      const cmd = String(event?.target?.getAttribute?.('data-cmd') || '').trim()
      if (!cmd || !inlineTextEditState?.element) return
      if (cmd === 'font-size') {
        const size = Math.max(8, Math.min(180, Number.parseInt(String(event?.target?.value || '16'), 10) || 16))
        applyInlineStyleToSelection('fontSize', `${size}px`)
      } else if (cmd === 'color') {
        const color = String(event?.target?.value || '#111111').trim() || '#111111'
        applyInlineStyleToSelection('color', color)
      }
      inlineTextEditState.element.focus()
    }, true)
  }
  visualTextToolbar = toolbar
  return toolbar
}

function positionTextToolbar() {
  if (!inlineTextEditState?.element || !visualTextToolbar) return
  const frameWindow = visualPreviewFrame.value?.contentWindow
  const rect = inlineTextEditState.element.getBoundingClientRect()
  const scrollX = Number(frameWindow?.scrollX || 0)
  const scrollY = Number(frameWindow?.scrollY || 0)
  const top = Math.max(4, Math.round(rect.top + scrollY - 38))
  const left = Math.max(4, Math.round(rect.left + scrollX))
  visualTextToolbar.style.display = 'inline-flex'
  visualTextToolbar.style.left = `${left}px`
  visualTextToolbar.style.top = `${top}px`
}

function hideTextToolbar() {
  if (visualTextToolbar) visualTextToolbar.style.display = 'none'
}

function applyInlineStyleToSelection(styleKey, styleValue) {
  const editState = inlineTextEditState
  if (!editState?.element || !visualFrameDocument) return
  const doc = visualFrameDocument
  const selection = doc.getSelection?.()
  const key = String(styleKey || '').trim()
  const value = String(styleValue || '').trim()
  if (!key || !value) return
  if (!selection || selection.rangeCount <= 0 || selection.isCollapsed) {
    editState.element.style[key] = value
    return
  }
  const range = selection.getRangeAt(0)
  const container = range.commonAncestorContainer?.nodeType === Node.ELEMENT_NODE
    ? range.commonAncestorContainer
    : range.commonAncestorContainer?.parentElement
  if (!container || !editState.element.contains(container)) {
    editState.element.style[key] = value
    return
  }
  const span = doc.createElement('span')
  span.style[key] = value
  try {
    const fragment = range.extractContents()
    span.appendChild(fragment)
    range.insertNode(span)
    selection.removeAllRanges()
    const nextRange = doc.createRange()
    nextRange.selectNodeContents(span)
    selection.addRange(nextRange)
  } catch {
    editState.element.style[key] = value
  }
}

async function finishInlineTextEditing(commit = true) {
  const editState = inlineTextEditState
  if (!editState?.element) {
    hideTextToolbar()
    return
  }
  const element = editState.element
  const nodeId = String(editState.nodeId || '').trim()
  if (editState.blurHandler) element.removeEventListener('blur', editState.blurHandler, true)
  if (editState.inputHandler) element.removeEventListener('input', editState.inputHandler, true)
  if (editState.keydownHandler) element.removeEventListener('keydown', editState.keydownHandler, true)
  element.removeAttribute('contenteditable')
  element.removeAttribute('data-mysite-inline-text')
  inlineTextEditState = null
  hideTextToolbar()

  if (!commit) return
  if (nodeId) {
    const selector = ensureLayerSelector(nodeId, element)
    if (selector) {
      const map = { ...visualOverridesMap.value }
      const layer = visualLayerIndex.value?.[nodeId]
      const existing = map[selector]
        ? { ...map[selector], styles: { ...(map[selector].styles || {}) } }
        : { selector, tag: layer?.tag || '', label: layer?.label || '', styles: {}, apply_text: false, text_content: '', apply_html: false, html_content: '' }
      const currentHtml = String(element.innerHTML || '')
      const currentText = String(element.textContent || '')
      const initialHtml = String(editState.initialHtml || '')
      const changed = currentHtml !== initialHtml
      if (changed) {
        if (currentHtml.trim()) {
          existing.apply_html = true
          existing.html_content = currentHtml
          existing.apply_text = false
          existing.text_content = ''
        } else {
          existing.apply_html = false
          existing.html_content = ''
          existing.apply_text = true
          existing.text_content = currentText
        }
        if (!existing.apply_text && !existing.apply_html && !Object.keys(existing.styles || {}).length) delete map[selector]
        else map[selector] = existing
        visualOverridesMap.value = map
      }
    }
  }
  rawHtmlInput.value = String(element.innerHTML || '')
  syncVisualPropsFromElement(element)
  nextTick(() => { syncResizeOverlay(); syncRedlineOverlay() })
  success.value = 'Inline text edit انجام شد.'
}

function startInlineTextEditing(element, options = {}) {
  if (!isInlineTextTarget(element)) return false
  if (!visualFrameDocument) return false
  const nodeId = ensureVisualNodeId(element)
  if (!visualLayerIndex.value[nodeId]) upsertSingleLayerForElement(element)
  if (inlineTextEditState?.element === element) {
    element.focus()
    positionTextToolbar()
    return true
  }
  void finishInlineTextEditing(true)
  pushVisualHistorySnapshot({ force: true })
  const toolbar = ensureTextToolbar(visualFrameDocument)
  if (!toolbar) return false
  const blurHandler = () => {
    window.setTimeout(() => {
      if (!inlineTextEditState?.element || inlineTextEditState.element !== element) return
      const active = visualFrameDocument.activeElement
      if (visualTextToolbar?.contains(active)) {
        element.focus()
        return
      }
      void finishInlineTextEditing(true)
    }, 80)
  }
  const inputHandler = () => {
    rawHtmlInput.value = String(element.innerHTML || '')
    syncVisualPropsFromElement(element)
    positionTextToolbar()
  }
  const keydownHandler = (event) => {
    const key = String(event?.key || '').toLowerCase()
    if (key === 'escape') {
      event.preventDefault()
      event.stopPropagation()
      void finishInlineTextEditing(true)
      return
    }
    if (key === 'enter' && !event.shiftKey && !event.metaKey && !event.ctrlKey) {
      event.preventDefault()
      event.stopPropagation()
      void finishInlineTextEditing(true)
    }
  }
  inlineTextEditState = { element, nodeId, blurHandler, inputHandler, keydownHandler }
  inlineTextEditState.initialHtml = String(element.innerHTML || '')
  element.setAttribute('contenteditable', 'true')
  element.setAttribute('data-mysite-inline-text', '1')
  element.addEventListener('blur', blurHandler, true)
  element.addEventListener('input', inputHandler, true)
  element.addEventListener('keydown', keydownHandler, true)
  if (options?.selectAll !== false) {
    const range = visualFrameDocument.createRange()
    range.selectNodeContents(element)
    const selection = visualFrameDocument.getSelection?.()
    selection?.removeAllRanges()
    selection?.addRange(range)
  }
  element.focus()
  positionTextToolbar()
  return true
}

function createElementForActiveTool(event) {
  const point = resolvePointerPointInFrame(event)
  return createElementByToolAtPoint(String(activeTool.value || 'select'), point)
}

function createElementByToolAtPoint(toolName, point) {
  if (!visualFrameDocument?.body) return ''
  const tool = String(toolName || 'select')
  if (!INSERTABLE_TOOLS.has(tool)) return ''
  pushVisualHistorySnapshot({ force: true })
  const element = visualFrameDocument.createElement(
    tool === 'text' ? 'p' : tool === 'component' ? 'article' : tool === 'comment' ? 'aside' : 'div'
  )
  element.style.position = 'absolute'
  element.style.left = `${Math.round(Number(point?.x || 0))}px`
  element.style.top = `${Math.round(Number(point?.y || 0))}px`
  element.style.zIndex = '10'

  if (tool === 'text') {
    element.textContent = 'Text'
    element.style.minWidth = '80px'
    element.style.minHeight = '24px'
    element.style.fontSize = '16px'
    element.style.color = '#0f172a'
  } else if (tool === 'rectangle') {
    element.style.width = '140px'
    element.style.height = '90px'
    element.style.background = 'rgba(13, 153, 255, 0.16)'
    element.style.border = '1px solid rgba(13, 153, 255, 0.88)'
    element.style.borderRadius = '10px'
  } else if (tool === 'frame') {
    element.style.width = '280px'
    element.style.height = '180px'
    element.style.background = 'rgba(16, 24, 40, 0.03)'
    element.style.border = '1px dashed rgba(59, 130, 246, 0.8)'
    element.style.borderRadius = '12px'
  } else if (tool === 'pen') {
    element.style.width = '150px'
    element.style.height = '2px'
    element.style.background = '#0d99ff'
    element.style.borderRadius = '999px'
  } else if (tool === 'comment') {
    element.style.width = '180px'
    element.style.minHeight = '74px'
    element.style.background = '#fff6d6'
    element.style.border = '1px solid #efc14a'
    element.style.borderRadius = '10px'
    element.style.padding = '10px'
    element.style.color = '#5f4500'
    element.style.fontSize = '13px'
    element.textContent = 'Comment'
  } else {
    element.style.width = '220px'
    element.style.minHeight = '120px'
    element.style.background = '#ffffff'
    element.style.border = '1px solid #d1d9e6'
    element.style.borderRadius = '12px'
    element.style.boxShadow = '0 10px 20px rgba(15, 23, 42, 0.12)'
    element.style.padding = '10px'
    element.textContent = 'Component'
  }

  visualFrameDocument.body.appendChild(element)
  const nodeId = upsertSingleLayerForElement(element)
  selectVisualLayer(nodeId)
  markVisualStructureDirty()
  success.value = 'المنت جدید روی بوم اضافه شد.'
  return nodeId
}

function detachFramePointerDragListeners(doc) {
  const targetDoc = doc || visualFrameDocument
  if (!targetDoc) return
  if (visualFramePointerMoveHandler) targetDoc.removeEventListener('mousemove', visualFramePointerMoveHandler, true)
  if (visualFramePointerUpHandler) targetDoc.removeEventListener('mouseup', visualFramePointerUpHandler, true)
  visualFramePointerMoveHandler = null
  visualFramePointerUpHandler = null
  frameDragState = null
  hideSmartGuides()
  hideFlowInsertionLine()
}

function detachResizeDragListeners(doc) {
  const targetDoc = doc || visualFrameDocument
  if (!targetDoc) return
  if (visualResizeMoveHandler) targetDoc.removeEventListener('mousemove', visualResizeMoveHandler, true)
  if (visualResizeUpHandler) targetDoc.removeEventListener('mouseup', visualResizeUpHandler, true)
  visualResizeMoveHandler = null
  visualResizeUpHandler = null
  resizeState = null
  rotateState = null
}

function ensureResizeOverlay(doc) {
  if (!doc?.body) return null
  let overlay = doc.getElementById('mysite-ve-resize-overlay')
  if (!overlay) {
    overlay = doc.createElement('div')
    overlay.id = 'mysite-ve-resize-overlay'
    overlay.style.display = 'none'
    const dirs = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w']
    for (const dir of dirs) {
      const handle = doc.createElement('button')
      handle.type = 'button'
      handle.className = `mysite-ve-resize-handle mysite-ve-resize-handle-${dir}`
      handle.setAttribute('data-dir', dir)
      handle.tabIndex = -1
      overlay.appendChild(handle)
    }
    const rotateLine = doc.createElement('div')
    rotateLine.className = 'mysite-ve-resize-rotate-line'
    overlay.appendChild(rotateLine)
    const rotateHandle = doc.createElement('button')
    rotateHandle.type = 'button'
    rotateHandle.className = 'mysite-ve-resize-handle mysite-ve-resize-handle-rotate'
    rotateHandle.setAttribute('data-dir', 'rotate')
    rotateHandle.tabIndex = -1
    overlay.appendChild(rotateHandle)
    doc.body.appendChild(overlay)
  }
  visualResizeOverlay = overlay
  return overlay
}

function hideResizeOverlay() {
  if (visualResizeOverlay) visualResizeOverlay.style.display = 'none'
}

function syncResizeOverlay() {
  if (!visualFrameDocument || !visualSelectedElement || !visualSelectedId.value) {
    hideResizeOverlay()
    positionTextToolbar()
    syncCanvasDecorOverlays()
    return
  }
  const overlay = ensureResizeOverlay(visualFrameDocument)
  if (!overlay) return
  const frameWin = visualPreviewFrame.value?.contentWindow
  if (!frameWin) return
  const zoom = Math.max(0.01, Number(canvasZoom.value || 1))
  const rect = visualSelectedElement.getBoundingClientRect()
  if (!rect || rect.width <= 0 || rect.height <= 0) {
    hideResizeOverlay()
    return
  }
  const left = Math.round((rect.left + Number(frameWin.scrollX || 0)) / zoom)
  const top = Math.round((rect.top + Number(frameWin.scrollY || 0)) / zoom)
  const width = Math.max(1, Math.round(rect.width / zoom))
  const height = Math.max(1, Math.round(rect.height / zoom))
  overlay.style.display = 'block'
  overlay.style.left = `${left}px`
  overlay.style.top = `${top}px`
  overlay.style.width = `${width}px`
  overlay.style.height = `${height}px`
  positionTextToolbar()
  syncCanvasDecorOverlays()
}

function ensureGuideOverlay(doc) {
  if (!doc?.body) return null
  let overlay = doc.getElementById('mysite-ve-guide-overlay')
  if (!overlay) {
    overlay = doc.createElement('div')
    overlay.id = 'mysite-ve-guide-overlay'
    const lineV = doc.createElement('div')
    lineV.className = 'mysite-ve-guide-line-v'
    const lineH = doc.createElement('div')
    lineH.className = 'mysite-ve-guide-line-h'
    const labelV = doc.createElement('div')
    labelV.className = 'mysite-ve-guide-label mysite-ve-guide-label-v'
    const labelH = doc.createElement('div')
    labelH.className = 'mysite-ve-guide-label mysite-ve-guide-label-h'
    overlay.appendChild(lineV)
    overlay.appendChild(lineH)
    overlay.appendChild(labelV)
    overlay.appendChild(labelH)
    doc.body.appendChild(overlay)
  }
  visualGuideOverlay = overlay
  visualGuideV = overlay.querySelector('.mysite-ve-guide-line-v')
  visualGuideH = overlay.querySelector('.mysite-ve-guide-line-h')
  visualGuideLabelV = overlay.querySelector('.mysite-ve-guide-label-v')
  visualGuideLabelH = overlay.querySelector('.mysite-ve-guide-label-h')
  return overlay
}

function ensureFlowInsertionLine(doc) {
  if (!doc?.body) return null
  let line = doc.getElementById('mysite-ve-flow-insertion-line')
  if (!line) {
    line = doc.createElement('div')
    line.id = 'mysite-ve-flow-insertion-line'
    doc.body.appendChild(line)
  }
  visualFlowInsertionLine = line
  return line
}

function showFlowInsertionLine(payload = {}) {
  if (!visualFrameDocument) return
  const line = ensureFlowInsertionLine(visualFrameDocument)
  if (!line) return
  const top = Number(payload?.top)
  const left = Number(payload?.left)
  const width = Number(payload?.width)
  if (!Number.isFinite(top) || !Number.isFinite(left) || !Number.isFinite(width)) {
    line.style.display = 'none'
    return
  }
  line.style.display = 'block'
  line.style.left = `${Math.round(left)}px`
  line.style.top = `${Math.round(top)}px`
  line.style.width = `${Math.max(24, Math.round(width))}px`
}

function hideFlowInsertionLine() {
  if (visualFlowInsertionLine) visualFlowInsertionLine.style.display = 'none'
}

function hideSmartGuides() {
  if (visualGuideV) visualGuideV.style.display = 'none'
  if (visualGuideH) visualGuideH.style.display = 'none'
  if (visualGuideLabelV) visualGuideLabelV.style.display = 'none'
  if (visualGuideLabelH) visualGuideLabelH.style.display = 'none'
}

function ensureMeasureOverlay(doc) {
  if (!doc?.body) return null
  let overlay = doc.getElementById('mysite-ve-measure-overlay')
  if (!overlay) {
    overlay = doc.createElement('div')
    overlay.id = 'mysite-ve-measure-overlay'
    const lineX = doc.createElement('div')
    lineX.className = 'mysite-ve-measure-line-x'
    const lineY = doc.createElement('div')
    lineY.className = 'mysite-ve-measure-line-y'
    const labelX = doc.createElement('div')
    labelX.className = 'mysite-ve-measure-label'
    const labelY = doc.createElement('div')
    labelY.className = 'mysite-ve-measure-label'
    overlay.appendChild(lineX)
    overlay.appendChild(lineY)
    overlay.appendChild(labelX)
    overlay.appendChild(labelY)
    doc.body.appendChild(overlay)
  }
  visualMeasureOverlay = overlay
  visualMeasureLineX = overlay.querySelector('.mysite-ve-measure-line-x')
  visualMeasureLineY = overlay.querySelector('.mysite-ve-measure-line-y')
  const labels = overlay.querySelectorAll('.mysite-ve-measure-label')
  visualMeasureLabelX = labels?.[0] || null
  visualMeasureLabelY = labels?.[1] || null
  return overlay
}

function hideMeasureOverlay() {
  if (visualMeasureOverlay) visualMeasureOverlay.style.display = 'none'
  handoffMeasureState.value = { visible: false, dx: null, dy: null, target: '' }
}

function showMeasureOverlay(payload) {
  if (!visualFrameDocument) return
  const overlay = ensureMeasureOverlay(visualFrameDocument)
  if (!overlay) return
  overlay.style.display = 'block'

  const dx = Number(payload?.dx)
  const dy = Number(payload?.dy)
  const targetLabel = String(payload?.target || '').trim()

  if (Number.isFinite(dx) && dx > 0 && visualMeasureLineX && visualMeasureLabelX) {
    const xStart = Math.round(Math.min(Number(payload?.x1 || 0), Number(payload?.x2 || 0)))
    const xEnd = Math.round(Math.max(Number(payload?.x1 || 0), Number(payload?.x2 || 0)))
    const y = Math.round(Number(payload?.xY || 0))
    visualMeasureLineX.style.display = 'block'
    visualMeasureLineX.style.left = `${xStart}px`
    visualMeasureLineX.style.top = `${y}px`
    visualMeasureLineX.style.width = `${Math.max(1, xEnd - xStart)}px`
    visualMeasureLabelX.style.display = 'block'
    visualMeasureLabelX.style.left = `${Math.round((xStart + xEnd) / 2)}px`
    visualMeasureLabelX.style.top = `${y - 8}px`
    visualMeasureLabelX.textContent = `${Math.round(dx)}px`
  } else {
    if (visualMeasureLineX) visualMeasureLineX.style.display = 'none'
    if (visualMeasureLabelX) visualMeasureLabelX.style.display = 'none'
  }

  if (Number.isFinite(dy) && dy > 0 && visualMeasureLineY && visualMeasureLabelY) {
    const yStart = Math.round(Math.min(Number(payload?.y1 || 0), Number(payload?.y2 || 0)))
    const yEnd = Math.round(Math.max(Number(payload?.y1 || 0), Number(payload?.y2 || 0)))
    const x = Math.round(Number(payload?.yX || 0))
    visualMeasureLineY.style.display = 'block'
    visualMeasureLineY.style.left = `${x}px`
    visualMeasureLineY.style.top = `${yStart}px`
    visualMeasureLineY.style.height = `${Math.max(1, yEnd - yStart)}px`
    visualMeasureLabelY.style.display = 'block'
    visualMeasureLabelY.style.left = `${x + 14}px`
    visualMeasureLabelY.style.top = `${Math.round((yStart + yEnd) / 2)}px`
    visualMeasureLabelY.textContent = `${Math.round(dy)}px`
  } else {
    if (visualMeasureLineY) visualMeasureLineY.style.display = 'none'
    if (visualMeasureLabelY) visualMeasureLabelY.style.display = 'none'
  }

  handoffMeasureState.value = {
    visible: true,
    dx: Number.isFinite(dx) ? Math.round(dx) : null,
    dy: Number.isFinite(dy) ? Math.round(dy) : null,
    target: targetLabel,
  }
}

function ensureRedlineOverlay(doc) {
  if (!doc?.body) return null
  let overlay = doc.getElementById('mysite-ve-redline-overlay')
  if (!overlay) {
    overlay = doc.createElement('div')
    overlay.id = 'mysite-ve-redline-overlay'
    const lineX = doc.createElement('div')
    lineX.className = 'mysite-ve-redline-line-x'
    const lineY = doc.createElement('div')
    lineY.className = 'mysite-ve-redline-line-y'
    const labelX = doc.createElement('div')
    labelX.className = 'mysite-ve-redline-label'
    const labelY = doc.createElement('div')
    labelY.className = 'mysite-ve-redline-label'
    overlay.appendChild(lineX)
    overlay.appendChild(lineY)
    overlay.appendChild(labelX)
    overlay.appendChild(labelY)
    doc.body.appendChild(overlay)
  }
  visualRedlineOverlay = overlay
  visualRedlineLineX = overlay.querySelector('.mysite-ve-redline-line-x')
  visualRedlineLineY = overlay.querySelector('.mysite-ve-redline-line-y')
  const labels = overlay.querySelectorAll('.mysite-ve-redline-label')
  visualRedlineLabelX = labels?.[0] || null
  visualRedlineLabelY = labels?.[1] || null
  return overlay
}

function hideRedlineOverlay() {
  if (visualRedlineOverlay) visualRedlineOverlay.style.display = 'none'
}

function showRedlineOverlay(redline) {
  if (!visualFrameDocument || !redline) { hideRedlineOverlay(); return }
  const overlay = ensureRedlineOverlay(visualFrameDocument)
  if (!overlay) return
  const boxA = redline?.node_a?.box
  const boxB = redline?.node_b?.box
  if (!boxA || !boxB) { hideRedlineOverlay(); return }
  overlay.style.display = 'block'

  const x1 = Number(boxA.centerX || 0)
  const y1 = Number(boxA.centerY || 0)
  const x2 = Number(boxB.centerX || 0)
  const y2 = Number(boxB.centerY || 0)
  const xStart = Math.min(x1, x2)
  const xEnd = Math.max(x1, x2)
  const yStart = Math.min(y1, y2)
  const yEnd = Math.max(y1, y2)

  if (visualRedlineLineX) {
    visualRedlineLineX.style.display = 'block'
    visualRedlineLineX.style.left = `${Math.round(xStart)}px`
    visualRedlineLineX.style.top = `${Math.round(y1)}px`
    visualRedlineLineX.style.width = `${Math.max(1, Math.round(xEnd - xStart))}px`
  }
  if (visualRedlineLineY) {
    visualRedlineLineY.style.display = 'block'
    visualRedlineLineY.style.left = `${Math.round(x2)}px`
    visualRedlineLineY.style.top = `${Math.round(yStart)}px`
    visualRedlineLineY.style.height = `${Math.max(1, Math.round(yEnd - yStart))}px`
  }
  if (visualRedlineLabelX) {
    visualRedlineLabelX.style.display = 'block'
    visualRedlineLabelX.style.left = `${Math.round((xStart + xEnd) / 2)}px`
    visualRedlineLabelX.style.top = `${Math.round(y1 - 10)}px`
    visualRedlineLabelX.textContent = `${Math.round(Math.abs(x2 - x1))}px`
  }
  if (visualRedlineLabelY) {
    visualRedlineLabelY.style.display = 'block'
    visualRedlineLabelY.style.left = `${Math.round(x2 + 14)}px`
    visualRedlineLabelY.style.top = `${Math.round((yStart + yEnd) / 2)}px`
    visualRedlineLabelY.textContent = `${Math.round(Math.abs(y2 - y1))}px`
  }
}

function syncRedlineOverlay() {
  if (String(mode.value || 'design') !== 'developer') {
    hideRedlineOverlay()
    return
  }
  showRedlineOverlay(handoffRedline.value)
}

function showSmartGuides(guides) {
  if (!visualFrameDocument) return
  ensureGuideOverlay(visualFrameDocument)
  const frameWindow = visualPreviewFrame.value?.contentWindow
  const scrollX = Number(frameWindow?.scrollX || 0)
  const scrollY = Number(frameWindow?.scrollY || 0)
  const selectedRect = visualSelectedElement?.getBoundingClientRect?.()
  const selectedTop = Number(selectedRect?.top || 0) + scrollY
  const selectedLeft = Number(selectedRect?.left || 0) + scrollX

  const x = Number(guides?.x)
  const y = Number(guides?.y)
  if (Number.isFinite(x) && visualGuideV) {
    const xPos = Math.round(x + scrollX)
    visualGuideV.style.display = 'block'
    visualGuideV.style.left = `${xPos}px`
    if (visualGuideLabelV) {
      visualGuideLabelV.style.display = 'block'
      visualGuideLabelV.style.left = `${xPos + 8}px`
      visualGuideLabelV.style.top = `${Math.max(10, Math.round(selectedTop + 6))}px`
      visualGuideLabelV.textContent = `${Math.round(x)}px`
    }
  } else if (visualGuideV) {
    visualGuideV.style.display = 'none'
    if (visualGuideLabelV) visualGuideLabelV.style.display = 'none'
  }
  if (Number.isFinite(y) && visualGuideH) {
    const yPos = Math.round(y + scrollY)
    visualGuideH.style.display = 'block'
    visualGuideH.style.top = `${yPos}px`
    if (visualGuideLabelH) {
      visualGuideLabelH.style.display = 'block'
      visualGuideLabelH.style.top = `${Math.max(10, yPos - 10)}px`
      visualGuideLabelH.style.left = `${Math.max(10, Math.round(selectedLeft + 8))}px`
      visualGuideLabelH.textContent = `${Math.round(y)}px`
    }
  } else if (visualGuideH) {
    visualGuideH.style.display = 'none'
    if (visualGuideLabelH) visualGuideLabelH.style.display = 'none'
  }
}

function onVisualFrameMouseMove(event) {
  if (String(mode.value || 'design') !== 'developer' || !event?.altKey || !visualSelectedElement || !visualFrameDocument) {
    hideMeasureOverlay()
    return
  }
  const baseTarget = resolveEventTargetElement(event?.target)
  const target = baseTarget?.closest?.('*')
  if (!target || !isVisualEditableElement(target) || target === visualSelectedElement || visualSelectedElement.contains(target)) {
    hideMeasureOverlay()
    return
  }
  const frameWindow = visualPreviewFrame.value?.contentWindow
  const scrollX = Number(frameWindow?.scrollX || 0)
  const scrollY = Number(frameWindow?.scrollY || 0)
  const a = visualSelectedElement.getBoundingClientRect()
  const b = target.getBoundingClientRect()

  let dx = null
  let x1 = null
  let x2 = null
  let xY = null
  if (a.right < b.left) {
    dx = b.left - a.right
    x1 = a.right + scrollX
    x2 = b.left + scrollX
    const overlapTop = Math.max(a.top, b.top)
    const overlapBottom = Math.min(a.bottom, b.bottom)
    xY = (overlapTop < overlapBottom ? ((overlapTop + overlapBottom) / 2) : ((a.top + a.bottom + b.top + b.bottom) / 4)) + scrollY
  } else if (b.right < a.left) {
    dx = a.left - b.right
    x1 = b.right + scrollX
    x2 = a.left + scrollX
    const overlapTop = Math.max(a.top, b.top)
    const overlapBottom = Math.min(a.bottom, b.bottom)
    xY = (overlapTop < overlapBottom ? ((overlapTop + overlapBottom) / 2) : ((a.top + a.bottom + b.top + b.bottom) / 4)) + scrollY
  }

  let dy = null
  let y1 = null
  let y2 = null
  let yX = null
  if (a.bottom < b.top) {
    dy = b.top - a.bottom
    y1 = a.bottom + scrollY
    y2 = b.top + scrollY
    const overlapLeft = Math.max(a.left, b.left)
    const overlapRight = Math.min(a.right, b.right)
    yX = (overlapLeft < overlapRight ? ((overlapLeft + overlapRight) / 2) : ((a.left + a.right + b.left + b.right) / 4)) + scrollX
  } else if (b.bottom < a.top) {
    dy = a.top - b.bottom
    y1 = b.bottom + scrollY
    y2 = a.top + scrollY
    const overlapLeft = Math.max(a.left, b.left)
    const overlapRight = Math.min(a.right, b.right)
    yX = (overlapLeft < overlapRight ? ((overlapLeft + overlapRight) / 2) : ((a.left + a.right + b.left + b.right) / 4)) + scrollX
  }

  if (!Number.isFinite(dx) && !Number.isFinite(dy)) {
    hideMeasureOverlay()
    return
  }

  showMeasureOverlay({
    dx,
    dy,
    x1,
    x2,
    xY,
    y1,
    y2,
    yX,
    target: nodeLabel(target),
  })
}

function ensureMarqueeOverlay(doc) {
  if (!doc?.body) return null
  let overlay = doc.getElementById('mysite-ve-marquee')
  if (!overlay) {
    overlay = doc.createElement('div')
    overlay.id = 'mysite-ve-marquee'
    doc.body.appendChild(overlay)
  }
  visualMarqueeOverlay = overlay
  return overlay
}

function hideMarqueeOverlay() {
  if (visualMarqueeOverlay) visualMarqueeOverlay.style.display = 'none'
}

function normalizeGuideItems(rows) {
  if (!Array.isArray(rows)) return []
  const out = []
  for (const row of rows) {
    const id = String(row?.id || '').trim()
    const axis = String(row?.axis || '').trim().toLowerCase()
    const value = Number(row?.value)
    if (!id || !Number.isFinite(value) || !['x', 'y'].includes(axis)) continue
    out.push({ id, axis, value: Math.max(0, Math.round(value)) })
  }
  return out
}

function ensureCanvasDecorOverlays(doc) {
  if (!doc?.body) return null
  if (!visualGridOverlay || !doc.getElementById('mysite-ve-grid-overlay')) {
    visualGridOverlay = doc.createElement('div')
    visualGridOverlay.id = 'mysite-ve-grid-overlay'
    doc.body.appendChild(visualGridOverlay)
  }
  if (!visualLayoutColumnsOverlay || !doc.getElementById('mysite-ve-layout-grid-overlay')) {
    visualLayoutColumnsOverlay = doc.createElement('div')
    visualLayoutColumnsOverlay.id = 'mysite-ve-layout-grid-overlay'
    doc.body.appendChild(visualLayoutColumnsOverlay)
  }
  if (!visualLayoutGuideLayer || !doc.getElementById('mysite-ve-layout-guides-layer')) {
    visualLayoutGuideLayer = doc.createElement('div')
    visualLayoutGuideLayer.id = 'mysite-ve-layout-guides-layer'
    doc.body.appendChild(visualLayoutGuideLayer)
  }
  if (!visualRulersOverlay || !doc.getElementById('mysite-ve-rulers')) {
    visualRulersOverlay = doc.createElement('div')
    visualRulersOverlay.id = 'mysite-ve-rulers'
    const topRuler = doc.createElement('div')
    topRuler.className = 'mysite-ve-ruler-top'
    topRuler.setAttribute('data-axis', 'x')
    const leftRuler = doc.createElement('div')
    leftRuler.className = 'mysite-ve-ruler-left'
    leftRuler.setAttribute('data-axis', 'y')
    visualRulersOverlay.appendChild(topRuler)
    visualRulersOverlay.appendChild(leftRuler)
    doc.body.appendChild(visualRulersOverlay)

    const onRulerDown = (event) => {
      if (Number(event?.button || 0) !== 0) return
      const axis = String(event?.currentTarget?.getAttribute?.('data-axis') || '').trim().toLowerCase()
      if (!axis || !['x', 'y'].includes(axis)) return
      event.preventDefault()
      event.stopPropagation()
      const frameWindow = visualPreviewFrame.value?.contentWindow
      const scrollX = Number(frameWindow?.scrollX || 0)
      const scrollY = Number(frameWindow?.scrollY || 0)
      const value = axis === 'x'
        ? Math.max(0, Math.round(Number(event.clientX || 0) + scrollX))
        : Math.max(0, Math.round(Number(event.clientY || 0) + scrollY))
      const id = `guide-${Math.random().toString(36).slice(2, 8)}`
      layoutGuideItems.value = [...normalizeGuideItems(layoutGuideItems.value), { id, axis, value }]
      renderPersistentGuideLines(doc)
      startPersistentGuideDrag({ id, axis }, event, doc)
    }
    topRuler.addEventListener('mousedown', onRulerDown, true)
    leftRuler.addEventListener('mousedown', onRulerDown, true)
  }
  return {
    grid: visualGridOverlay,
    columns: visualLayoutColumnsOverlay,
    rulers: visualRulersOverlay,
    guides: visualLayoutGuideLayer,
  }
}

function removeGuideById(guideId) {
  const id = String(guideId || '').trim()
  if (!id) return
  layoutGuideItems.value = normalizeGuideItems(layoutGuideItems.value).filter((row) => row.id !== id)
}

function startPersistentGuideDrag(guide, pointerDownEvent, doc) {
  const guideId = String(guide?.id || '').trim()
  const axis = String(guide?.axis || '').trim().toLowerCase()
  if (!guideId || !['x', 'y'].includes(axis) || !doc) return
  const frameWindow = visualPreviewFrame.value?.contentWindow
  const onMove = (moveEvent) => {
    const scrollX = Number(frameWindow?.scrollX || 0)
    const scrollY = Number(frameWindow?.scrollY || 0)
    const value = axis === 'x'
      ? Math.max(0, Math.round(Number(moveEvent.clientX || 0) + scrollX))
      : Math.max(0, Math.round(Number(moveEvent.clientY || 0) + scrollY))
    layoutGuideItems.value = normalizeGuideItems(layoutGuideItems.value).map((row) =>
      row.id === guideId ? { ...row, value } : row
    )
    renderPersistentGuideLines(doc)
  }
  const onUp = (upEvent) => {
    if (axis === 'x' && Number(upEvent?.clientY || 0) < 4) removeGuideById(guideId)
    if (axis === 'y' && Number(upEvent?.clientX || 0) < 4) removeGuideById(guideId)
    if (visualGuideDragMoveHandler) doc.removeEventListener('mousemove', visualGuideDragMoveHandler, true)
    if (visualGuideDragUpHandler) doc.removeEventListener('mouseup', visualGuideDragUpHandler, true)
    visualGuideDragMoveHandler = null
    visualGuideDragUpHandler = null
    renderPersistentGuideLines(doc)
  }
  visualGuideDragMoveHandler = onMove
  visualGuideDragUpHandler = onUp
  doc.addEventListener('mousemove', visualGuideDragMoveHandler, true)
  doc.addEventListener('mouseup', visualGuideDragUpHandler, true)
  pointerDownEvent?.preventDefault?.()
}

function renderPersistentGuideLines(doc) {
  if (!doc || !visualLayoutGuideLayer) return
  while (visualLayoutGuideLayer.firstChild) visualLayoutGuideLayer.removeChild(visualLayoutGuideLayer.firstChild)
  const rows = normalizeGuideItems(layoutGuideItems.value)
  for (const row of rows) {
    const line = doc.createElement('div')
    line.className = `mysite-ve-guide-persistent mysite-ve-guide-persistent-${row.axis === 'x' ? 'v' : 'h'}`
    line.setAttribute('data-guide-id', row.id)
    line.style.display = showLayoutGuides.value ? 'block' : 'none'
    if (row.axis === 'x') line.style.left = `${Math.round(row.value)}px`
    else line.style.top = `${Math.round(row.value)}px`
    line.addEventListener('mousedown', (event) => {
      if (Number(event?.button || 0) !== 0) return
      event.preventDefault()
      event.stopPropagation()
      startPersistentGuideDrag(row, event, doc)
    }, true)
    line.addEventListener('dblclick', (event) => {
      event.preventDefault()
      event.stopPropagation()
      removeGuideById(row.id)
      renderPersistentGuideLines(doc)
    }, true)
    visualLayoutGuideLayer.appendChild(line)
  }
}

function syncCanvasDecorOverlays() {
  if (!visualFrameDocument) return
  const overlays = ensureCanvasDecorOverlays(visualFrameDocument)
  if (!overlays) return
  const frameWindow = visualPreviewFrame.value?.contentWindow
  const scrollX = Number(frameWindow?.scrollX || 0)
  const scrollY = Number(frameWindow?.scrollY || 0)
  const viewportWidth = Number(frameWindow?.innerWidth || 0)
  const viewportHeight = Number(frameWindow?.innerHeight || 0)
  const bodyWidth = Math.max(
    Number(visualFrameDocument.documentElement?.scrollWidth || 0),
    Number(visualFrameDocument.body?.scrollWidth || 0),
    viewportWidth
  )
  const bodyHeight = Math.max(
    Number(visualFrameDocument.documentElement?.scrollHeight || 0),
    Number(visualFrameDocument.body?.scrollHeight || 0),
    viewportHeight
  )

  for (const overlay of [overlays.grid, overlays.columns, overlays.guides]) {
    if (!overlay) continue
    overlay.style.width = `${Math.max(0, Math.round(bodyWidth))}px`
    overlay.style.height = `${Math.max(0, Math.round(bodyHeight))}px`
    overlay.style.left = '0px'
    overlay.style.top = '0px'
  }

  if (overlays.grid) {
    const size = Math.max(2, Number(gridSize.value || 8))
    overlays.grid.style.display = showPixelGrid.value ? 'block' : 'none'
    overlays.grid.style.backgroundImage = `repeating-linear-gradient(to right, rgba(13,153,255,0.14) 0, rgba(13,153,255,0.14) 1px, transparent 1px, transparent ${size}px), repeating-linear-gradient(to bottom, rgba(13,153,255,0.14) 0, rgba(13,153,255,0.14) 1px, transparent 1px, transparent ${size}px)`
  }

  if (overlays.columns) {
    const cols = Math.max(1, Number(layoutGridColumns.value || 12))
    const colWidthPercent = 100 / cols
    overlays.columns.style.display = showLayoutGrid.value ? 'block' : 'none'
    overlays.columns.style.backgroundImage = `repeating-linear-gradient(to right, rgba(13,153,255,0.11) 0 calc(${colWidthPercent}% - 12px), transparent calc(${colWidthPercent}% - 12px) ${colWidthPercent}%)`
  }

  if (overlays.rulers) {
    const topRuler = overlays.rulers.querySelector('.mysite-ve-ruler-top')
    const leftRuler = overlays.rulers.querySelector('.mysite-ve-ruler-left')
    overlays.rulers.style.display = showRulers.value ? 'block' : 'none'
    if (topRuler) {
      topRuler.style.top = `${Math.round(scrollY)}px`
      topRuler.style.left = `${Math.round(18 + scrollX)}px`
      topRuler.style.width = `${Math.max(0, Math.round(viewportWidth - 18))}px`
    }
    if (leftRuler) {
      leftRuler.style.left = `${Math.round(scrollX)}px`
      leftRuler.style.top = `${Math.round(18 + scrollY)}px`
      leftRuler.style.height = `${Math.max(0, Math.round(viewportHeight - 18))}px`
    }
  }

  if (overlays.guides) overlays.guides.style.display = showLayoutGuides.value ? 'block' : 'none'
  renderPersistentGuideLines(visualFrameDocument)
}

function selectByMarqueeRect(rect) {
  if (!visualFrameDocument) return
  const selectedIds = []
  const frameWindow = visualPreviewFrame.value?.contentWindow
  const scrollX = Number(frameWindow?.scrollX || 0)
  const scrollY = Number(frameWindow?.scrollY || 0)
  const all = Array.from(visualFrameDocument.body.querySelectorAll('*')).filter((row) => isVisualEditableElement(row))
  for (const element of all) {
    const b = element.getBoundingClientRect()
    const left = b.left + scrollX
    const right = b.right + scrollX
    const top = b.top + scrollY
    const bottom = b.bottom + scrollY
    if (right < rect.left || left > rect.right || bottom < rect.top || top > rect.bottom) continue
    const id = ensureVisualNodeId(element)
    if (!visualLayerIndex.value[id]) upsertSingleLayerForElement(element)
    selectedIds.push(id)
  }
  if (!selectedIds.length) {
    clearVisualSelection()
    return
  }
  const primaryId = selectedIds[selectedIds.length - 1]
  visualSelectedIds.value = selectedIds
  visualSelectedId.value = primaryId
  visualSelectedElement = getVisualElementById(primaryId)
  applySelectionClasses()
  if (visualSelectedElement) {
    rawHtmlInput.value = String(visualSelectedElement.innerHTML || '')
    syncVisualPropsFromElement(visualSelectedElement)
  }
}

function startMarqueeSelection(event, doc) {
  const frameWindow = visualPreviewFrame.value?.contentWindow
  const scrollX = Number(frameWindow?.scrollX || 0)
  const scrollY = Number(frameWindow?.scrollY || 0)
  const startX = Number(event.clientX || 0) + scrollX
  const startY = Number(event.clientY || 0) + scrollY
  marqueeState = { startX, startY, lastRect: { left: startX, right: startX, top: startY, bottom: startY } }
  const overlay = ensureMarqueeOverlay(doc)
  if (!overlay) return
  overlay.style.display = 'block'
  overlay.style.left = `${Math.round(startX)}px`
  overlay.style.top = `${Math.round(startY)}px`
  overlay.style.width = '1px'
  overlay.style.height = '1px'

  visualMarqueeMoveHandler = (moveEvent) => {
    if (!marqueeState || !visualMarqueeOverlay) return
    const currentX = Number(moveEvent.clientX || 0) + Number(frameWindow?.scrollX || 0)
    const currentY = Number(moveEvent.clientY || 0) + Number(frameWindow?.scrollY || 0)
    const left = Math.min(marqueeState.startX, currentX)
    const right = Math.max(marqueeState.startX, currentX)
    const top = Math.min(marqueeState.startY, currentY)
    const bottom = Math.max(marqueeState.startY, currentY)
    marqueeState.lastRect = { left, right, top, bottom }
    visualMarqueeOverlay.style.display = 'block'
    visualMarqueeOverlay.style.left = `${Math.round(left)}px`
    visualMarqueeOverlay.style.top = `${Math.round(top)}px`
    visualMarqueeOverlay.style.width = `${Math.max(1, Math.round(right - left))}px`
    visualMarqueeOverlay.style.height = `${Math.max(1, Math.round(bottom - top))}px`
  }

  visualMarqueeUpHandler = () => {
    const rect = marqueeState?.lastRect
    if (rect) selectByMarqueeRect(rect)
    suppressFrameClickOnce = true
    if (visualMarqueeMoveHandler) doc.removeEventListener('mousemove', visualMarqueeMoveHandler, true)
    if (visualMarqueeUpHandler) doc.removeEventListener('mouseup', visualMarqueeUpHandler, true)
    visualMarqueeMoveHandler = null
    visualMarqueeUpHandler = null
    marqueeState = null
    hideMarqueeOverlay()
  }

  doc.addEventListener('mousemove', visualMarqueeMoveHandler, true)
  doc.addEventListener('mouseup', visualMarqueeUpHandler, true)
}

function computeSmartGuideSnapState(target, desiredLeft, desiredTop) {
  const frameWindow = visualPreviewFrame.value?.contentWindow
  if (!frameWindow || !target?.parentElement) return { left: desiredLeft, top: desiredTop, guideX: null, guideY: null }
  const zoom = Math.max(0.01, Number(canvasZoom.value || 1))
  const startRect = target.getBoundingClientRect()
  const candidateLeft = startRect.left + ((desiredLeft - (Number.parseFloat(target.style.left || '0') || 0)) * zoom)
  const candidateTop = startRect.top + ((desiredTop - (Number.parseFloat(target.style.top || '0') || 0)) * zoom)
  const width = startRect.width
  const height = startRect.height
  const candidate = {
    left: candidateLeft,
    centerX: candidateLeft + (width / 2),
    right: candidateLeft + width,
    top: candidateTop,
    centerY: candidateTop + (height / 2),
    bottom: candidateTop + height,
  }
  const parentRect = target.parentElement.getBoundingClientRect()
  const xTargets = [parentRect.left, parentRect.left + (parentRect.width / 2), parentRect.right]
  const yTargets = [parentRect.top, parentRect.top + (parentRect.height / 2), parentRect.bottom]
  if (showLayoutGuides.value) {
    const guides = normalizeGuideItems(layoutGuideItems.value)
    for (const guide of guides) {
      if (guide.axis === 'x') xTargets.push(guide.value)
      else yTargets.push(guide.value)
    }
  }
  const siblings = Array.from(target.parentElement.children || []).filter((row) => row !== target && isVisualEditableElement(row))
  for (const sibling of siblings) {
    const rect = sibling.getBoundingClientRect()
    xTargets.push(rect.left, rect.left + (rect.width / 2), rect.right)
    yTargets.push(rect.top, rect.top + (rect.height / 2), rect.bottom)
  }
  const threshold = 6
  let bestX = null
  let bestY = null
  const candidateX = [candidate.left, candidate.centerX, candidate.right]
  const candidateY = [candidate.top, candidate.centerY, candidate.bottom]
  for (const x of xTargets) {
    for (const c of candidateX) {
      const d = x - c
      if (Math.abs(d) <= threshold && (!bestX || Math.abs(d) < Math.abs(bestX.delta))) bestX = { delta: d, line: x }
    }
  }
  for (const y of yTargets) {
    for (const c of candidateY) {
      const d = y - c
      if (Math.abs(d) <= threshold && (!bestY || Math.abs(d) < Math.abs(bestY.delta))) bestY = { delta: d, line: y }
    }
  }
  return {
    left: Math.round(desiredLeft + (Number(bestX?.delta || 0) / zoom)),
    top: Math.round(desiredTop + (Number(bestY?.delta || 0) / zoom)),
    guideX: bestX?.line ?? null,
    guideY: bestY?.line ?? null,
  }
}

function splitTransformRotation(transformText) {
  const source = String(transformText || '').trim()
  if (!source) return { base: '', rotateDeg: 0 }
  const rotateMatch = source.match(/rotate\(\s*(-?\d+(?:\.\d+)?)deg\s*\)/i)
  const rotateDeg = rotateMatch ? Number.parseFloat(rotateMatch[1]) || 0 : 0
  const base = source.replace(/rotate\(\s*-?\d+(?:\.\d+)?deg\s*\)/ig, '').replace(/\s+/g, ' ').trim()
  return { base, rotateDeg }
}

function isBalancedMathExpression(text) {
  const source = String(text || '')
  let depth = 0
  for (let i = 0; i < source.length; i += 1) {
    const ch = source[i]
    if (ch === '(') depth += 1
    if (ch === ')') {
      depth -= 1
      if (depth < 0) return false
    }
  }
  return depth === 0
}

function evaluateMathNumericExpression(text) {
  const source = String(text || '').trim()
  if (!source) return null
  if (!/^[0-9+\-*/().\s]+$/.test(source)) return null
  if (!isBalancedMathExpression(source)) return null
  const compact = source.replace(/\s+/g, '')
  if (!compact || /[+\-*/.]$/.test(compact)) return null
  try {
    const result = Function(`"use strict"; return (${compact})`)()
    return Number.isFinite(result) ? result : null
  } catch {
    return null
  }
}

function parseRotationInput(value) {
  const raw = String(value ?? '').trim()
  if (!raw) return { empty: true, valid: true, deg: 0 }
  const withoutUnit = raw.replace(/deg$/i, '').trim()
  const direct = Number.parseFloat(withoutUnit)
  if (Number.isFinite(direct)) return { empty: false, valid: true, deg: Math.round(direct * 10) / 10 }
  const evaluated = evaluateMathNumericExpression(withoutUnit)
  if (!Number.isFinite(evaluated)) return { empty: false, valid: false, deg: 0 }
  return { empty: false, valid: true, deg: Math.round(evaluated * 10) / 10 }
}

function startRotateByHandle(event, targetDoc) {
  if (!visualSelectedElement || !visualSelectedId.value) return
  pushVisualHistorySnapshot({ force: true })
  const element = visualSelectedElement
  const rect = element.getBoundingClientRect()
  const centerX = rect.left + (rect.width / 2)
  const centerY = rect.top + (rect.height / 2)
  const current = splitTransformRotation(element.style.transform)
  rotateState = {
    nodeId: String(visualSelectedId.value || ''),
    element,
    centerX,
    centerY,
    baseTransform: current.base,
    angle: current.rotateDeg,
    moved: false,
  }

  visualResizeMoveHandler = (moveEvent) => {
    if (!rotateState?.element) return
    const dx = Number(moveEvent.clientX || 0) - rotateState.centerX
    const dy = Number(moveEvent.clientY || 0) - rotateState.centerY
    let deg = (Math.atan2(dy, dx) * 180 / Math.PI) + 90
    if (moveEvent.shiftKey) deg = Math.round(deg / 15) * 15
    rotateState.angle = Math.round(deg * 10) / 10
    rotateState.moved = true
    const base = String(rotateState.baseTransform || '').trim()
    rotateState.element.style.transform = `${base ? `${base} ` : ''}rotate(${rotateState.angle}deg)`.trim()
    syncResizeOverlay()
  }

  visualResizeUpHandler = () => {
    const state = rotateState
    rotateState = null
    detachResizeDragListeners(targetDoc)
    if (!state?.moved) return
    applyStyleBatchForNodes([state.nodeId], [
      { key: 'transform', value: `${state.baseTransform ? `${state.baseTransform} ` : ''}rotate(${state.angle}deg)`.trim() },
    ])
    success.value = 'زاویه المنت به‌روزرسانی شد.'
  }

  targetDoc.addEventListener('mousemove', visualResizeMoveHandler, true)
  targetDoc.addEventListener('mouseup', visualResizeUpHandler, true)
}

function startResizeByHandle(direction, event, targetDoc) {
  if (!visualSelectedElement) return
  if (isLayerLockedElement(visualSelectedElement)) return
  const dir = String(direction || '').trim().toLowerCase()
  if (!dir) return
  pushVisualHistorySnapshot({ force: true })
  const element = visualSelectedElement
  const frameWin = visualPreviewFrame.value?.contentWindow
  const computedPos = String(frameWin?.getComputedStyle?.(element)?.position || element.style.position || '').trim()
  if ((dir.includes('w') || dir.includes('n')) && (!computedPos || computedPos === 'static')) {
    element.style.position = 'relative'
    applyVisualField('position', 'relative')
  }
  const zoom = Math.max(0.01, Number(canvasZoom.value || 1))
  const startRect = element.getBoundingClientRect()
  const startWidth = Math.max(1, Math.round(startRect.width / zoom))
  const startHeight = Math.max(1, Math.round(startRect.height / zoom))
  const startLeft = Number.parseFloat(element.style.left || '0') || 0
  const startTop = Number.parseFloat(element.style.top || '0') || 0
  resizeState = {
    dir,
    nodeId: String(visualSelectedId.value || ''),
    element,
    startX: Number(event.clientX || 0),
    startY: Number(event.clientY || 0),
    startWidth,
    startHeight,
    startLeft,
    startTop,
    startCenterX: startLeft + (startWidth / 2),
    startCenterY: startTop + (startHeight / 2),
    startAspect: Math.max(0.01, Math.round((startWidth / Math.max(1, startHeight)) * 10000) / 10000),
    nextWidth: startWidth,
    nextHeight: startHeight,
    nextLeft: startLeft,
    nextTop: startTop,
  }

  visualResizeMoveHandler = (moveEvent) => {
    if (!resizeState?.element) return
    const zoom = Math.max(0.01, Number(canvasZoom.value || 1))
    const dx = (Number(moveEvent.clientX || 0) - resizeState.startX) / zoom
    const dy = (Number(moveEvent.clientY || 0) - resizeState.startY) / zoom
    let width = resizeState.startWidth
    let height = resizeState.startHeight
    let left = resizeState.startLeft
    let top = resizeState.startTop
    if (dir.includes('e')) width = Math.max(20, resizeState.startWidth + dx)
    if (dir.includes('s')) height = Math.max(20, resizeState.startHeight + dy)
    if (dir.includes('w')) {
      width = Math.max(20, resizeState.startWidth - dx)
      left = resizeState.startLeft + (resizeState.startWidth - width)
    }
    if (dir.includes('n')) {
      height = Math.max(20, resizeState.startHeight - dy)
      top = resizeState.startTop + (resizeState.startHeight - height)
    }

    if (moveEvent.shiftKey) {
      const aspect = Math.max(0.01, Number(resizeState.startAspect || 1))
      const widthDelta = Math.abs(width - resizeState.startWidth)
      const heightDelta = Math.abs(height - resizeState.startHeight)
      if ((dir.includes('e') || dir.includes('w')) && (!dir.includes('n') && !dir.includes('s') || widthDelta >= heightDelta)) {
        height = Math.max(20, width / aspect)
        if (dir.includes('n')) top = resizeState.startTop + (resizeState.startHeight - height)
      } else {
        width = Math.max(20, height * aspect)
        if (dir.includes('w')) left = resizeState.startLeft + (resizeState.startWidth - width)
      }
    }

    if (moveEvent.altKey) {
      if (dir.includes('e') || dir.includes('w')) left = resizeState.startCenterX - (width / 2)
      if (dir.includes('n') || dir.includes('s')) top = resizeState.startCenterY - (height / 2)
    }

    resizeState.nextWidth = Math.round(width)
    resizeState.nextHeight = Math.round(height)
    resizeState.nextLeft = Math.round(left)
    resizeState.nextTop = Math.round(top)
    resizeState.element.style.width = `${resizeState.nextWidth}px`
    resizeState.element.style.height = `${resizeState.nextHeight}px`
    if (dir.includes('w') || moveEvent.altKey) resizeState.element.style.left = `${resizeState.nextLeft}px`
    if (dir.includes('n') || moveEvent.altKey) resizeState.element.style.top = `${resizeState.nextTop}px`
    syncResizeOverlay()
  }

  visualResizeUpHandler = () => {
    const state = resizeState
    detachResizeDragListeners(targetDoc)
    if (!state) return
    const batch = [
      { key: 'width', value: `${state.nextWidth}px` },
      { key: 'height', value: `${state.nextHeight}px` },
    ]
    if (state.dir.includes('w') || state.nextLeft !== state.startLeft) batch.push({ key: 'left', value: `${state.nextLeft}px` })
    if (state.dir.includes('n') || state.nextTop !== state.startTop) batch.push({ key: 'top', value: `${state.nextTop}px` })
    applyStyleBatchForNodes([state.nodeId], batch)
    syncResizeOverlay()
    success.value = 'ابعاد المنت به‌روزرسانی شد.'
  }

  targetDoc.addEventListener('mousemove', visualResizeMoveHandler, true)
  targetDoc.addEventListener('mouseup', visualResizeUpHandler, true)
}

function detachCanvasPanListeners(doc) {
  const targetDoc = doc || visualFrameDocument
  if (!targetDoc) return
  if (visualFramePointerMoveHandler) targetDoc.removeEventListener('mousemove', visualFramePointerMoveHandler, true)
  if (visualFramePointerUpHandler) targetDoc.removeEventListener('mouseup', visualFramePointerUpHandler, true)
  visualFramePointerMoveHandler = null
  visualFramePointerUpHandler = null
  framePanState = null
}

function startCanvasPan(event, doc) {
  const frameWindow = visualPreviewFrame.value?.contentWindow
  if (!frameWindow || !doc) return
  framePanState = {
    startX: Number(event.clientX || 0),
    startY: Number(event.clientY || 0),
    scrollX: Number(frameWindow.scrollX || 0),
    scrollY: Number(frameWindow.scrollY || 0),
  }
  visualFramePointerMoveHandler = (moveEvent) => {
    if (!framePanState) return
    const dx = Number(moveEvent.clientX || 0) - framePanState.startX
    const dy = Number(moveEvent.clientY || 0) - framePanState.startY
    try {
      frameWindow.scrollTo({ left: framePanState.scrollX - dx, top: framePanState.scrollY - dy, behavior: 'auto' })
    } catch {
      frameWindow.scrollTo(framePanState.scrollX - dx, framePanState.scrollY - dy)
    }
    syncResizeOverlay()
    syncCanvasDecorOverlays()
  }
  visualFramePointerUpHandler = () => {
    detachCanvasPanListeners(doc)
  }
  doc.addEventListener('mousemove', visualFramePointerMoveHandler, true)
  doc.addEventListener('mouseup', visualFramePointerUpHandler, true)
}

function onVisualFramePointerDown(event) {
  if (Number(event?.button || 0) !== 0) return
  if (canvasSpacePressed && visualFrameDocument) {
    event.preventDefault()
    event.stopPropagation()
    startCanvasPan(event, visualFrameDocument)
    return
  }
  if (String(activeTool.value || 'select') !== 'select') return
  const initialTarget = resolveEventTargetElement(event?.target)
  if (!initialTarget) return
  const resizeHandle = initialTarget.closest?.('.mysite-ve-resize-handle')
  if (resizeHandle && visualFrameDocument) {
    event.preventDefault()
    event.stopPropagation()
    const dir = String(resizeHandle.getAttribute('data-dir') || '').trim().toLowerCase()
    if (dir === 'rotate') startRotateByHandle(event, visualFrameDocument)
    else startResizeByHandle(dir, event, visualFrameDocument)
    return
  }
  const blankArea =
    initialTarget === visualFrameDocument?.body ||
    initialTarget === visualFrameDocument?.documentElement
  if (blankArea && visualFrameDocument) {
    event.preventDefault()
    event.stopPropagation()
    startMarqueeSelection(event, visualFrameDocument)
    return
  }
  const target = initialTarget.closest('*')
  if (!isVisualEditableElement(target)) return
  if (isLayerLockedElement(target)) return
  const targetId = ensureVisualNodeId(target)
  if (!visualSelectedIds.value.includes(targetId)) return
  if (!visualSelectedElement || target !== visualSelectedElement) {
    selectVisualLayer(targetId)
  }

  event.preventDefault()
  event.stopPropagation()
  pushVisualHistorySnapshot({ force: true })

  const frameWindow = visualPreviewFrame.value?.contentWindow
  const computedPosition = String(frameWindow?.getComputedStyle?.(target)?.position || target.style.position || '').trim()
  const isFlowSnapMode = !['absolute', 'fixed'].includes(computedPosition)
  const doc = target.ownerDocument

  if (isFlowSnapMode) {
    const parent = target.parentElement
    frameDragState = {
      mode: 'flow',
      nodeId: String(visualSelectedId.value || ''),
      element: target,
      parent,
      moved: false,
      referenceNode: null,
      appendToEnd: false,
    }

    visualFramePointerMoveHandler = (moveEvent) => {
      if (!frameDragState?.element || !frameDragState?.parent) return
      const dragTarget = frameDragState.element
      const siblings = Array.from(frameDragState.parent.children || []).filter((row) => row !== dragTarget && isVisualEditableElement(row))
      if (!siblings.length) {
        hideFlowInsertionLine()
        return
      }
      const pointerY = Number(moveEvent.clientY || 0)
      let reference = null
      for (const sibling of siblings) {
        const rect = sibling.getBoundingClientRect()
        const mid = rect.top + (rect.height / 2)
        if (pointerY < mid) {
          reference = sibling
          break
        }
      }
      const frameWindow = visualPreviewFrame.value?.contentWindow
      const scrollX = Number(frameWindow?.scrollX || 0)
      const scrollY = Number(frameWindow?.scrollY || 0)
      const parentRect = frameDragState.parent.getBoundingClientRect()
      frameDragState.referenceNode = reference
      frameDragState.appendToEnd = !reference
      if (reference) {
        const refRect = reference.getBoundingClientRect()
        showFlowInsertionLine({
          left: parentRect.left + scrollX,
          top: refRect.top + scrollY,
          width: parentRect.width,
        })
        frameDragState.moved = reference !== dragTarget.nextElementSibling
      } else {
        const lastSibling = siblings[siblings.length - 1]
        const lastRect = lastSibling?.getBoundingClientRect?.()
        showFlowInsertionLine({
          left: parentRect.left + scrollX,
          top: Number(lastRect?.bottom || parentRect.bottom) + scrollY,
          width: parentRect.width,
        })
        frameDragState.moved = dragTarget !== frameDragState.parent.lastElementChild
      }
    }

    visualFramePointerUpHandler = async () => {
      const moved = Boolean(frameDragState?.moved)
      const focusNodeId = String(frameDragState?.nodeId || '')
      const parentNode = frameDragState?.parent || null
      const dragTarget = frameDragState?.element || null
      const reference = frameDragState?.referenceNode || null
      const appendToEnd = Boolean(frameDragState?.appendToEnd)
      if (moved && parentNode && dragTarget) {
        if (appendToEnd) parentNode.appendChild(dragTarget)
        else if (reference) parentNode.insertBefore(dragTarget, reference)
        markVisualStructureDirty()
      }
      detachFramePointerDragListeners(doc)
      if (!moved || !visualFrameDocument) return
      await runVisualLayerScan(visualFrameDocument, {
        loadToken: previewFrameLoadToken,
        focusNodeId,
      })
      if (focusNodeId) selectVisualLayer(focusNodeId)
      success.value = 'جایگاه المنت با حالت Auto snap به‌روزرسانی شد.'
    }

    doc.addEventListener('mousemove', visualFramePointerMoveHandler, true)
    doc.addEventListener('mouseup', visualFramePointerUpHandler, true)
    return
  }

  const currentPosition = String(target.style.position || '').trim()
  if (!currentPosition || currentPosition === 'static') {
    target.style.position = 'relative'
    applyVisualField('position', 'relative')
  }

  const startLeft = Number.parseFloat(target.style.left || '0') || 0
  const startTop = Number.parseFloat(target.style.top || '0') || 0

  frameDragState = {
    mode: 'free',
    nodeId: String(visualSelectedId.value || ''),
    element: target,
    startX: Number(event.clientX || 0),
    startY: Number(event.clientY || 0),
    startLeft,
    startTop,
    lastLeft: startLeft,
    lastTop: startTop,
    moved: false,
  }

  visualFramePointerMoveHandler = (moveEvent) => {
    if (!frameDragState?.element) return
    const zoom = Math.max(0.01, Number(canvasZoom.value || 1))
    const dx = (Number(moveEvent.clientX || 0) - frameDragState.startX) / zoom
    const dy = (Number(moveEvent.clientY || 0) - frameDragState.startY) / zoom
    const desiredLeft = Math.round(frameDragState.startLeft + dx)
    const desiredTop = Math.round(frameDragState.startTop + dy)
    const snapState = computeSmartGuideSnapState(frameDragState.element, desiredLeft, desiredTop)
    const nextLeft = snapState.left
    const nextTop = snapState.top

    frameDragState.lastLeft = nextLeft
    frameDragState.lastTop = nextTop
    frameDragState.moved = frameDragState.moved || Math.abs(dx) > 1 || Math.abs(dy) > 1

    frameDragState.element.style.left = `${nextLeft}px`
    frameDragState.element.style.top = `${nextTop}px`
    showSmartGuides({ x: snapState.guideX, y: snapState.guideY })
  }

  visualFramePointerUpHandler = () => {
    if (frameDragState?.moved) {
      applyVisualField('left', `${frameDragState.lastLeft}px`)
      applyVisualField('top', `${frameDragState.lastTop}px`)
      success.value = 'موقعیت المنت به‌روزرسانی شد.'
    }
    detachFramePointerDragListeners(doc)
  }

  doc.addEventListener('mousemove', visualFramePointerMoveHandler, true)
  doc.addEventListener('mouseup', visualFramePointerUpHandler, true)
}

function onVisualFrameClick(event) {
  if (suppressFrameClickOnce) {
    suppressFrameClickOnce = false
    event.preventDefault()
    event.stopPropagation()
    return
  }
  const initialTarget = resolveEventTargetElement(event?.target)
  if (!initialTarget) return
  if (initialTarget === visualFrameDocument?.body || initialTarget === visualFrameDocument?.documentElement) {
    clearVisualSelection()
    return
  }
  const target = initialTarget.closest('*')
  if (!isVisualEditableElement(target)) return
  if (isLayerLockedElement(target)) {
    event.preventDefault()
    event.stopPropagation()
    success.value = 'این لایه قفل است. برای ویرایش، ابتدا قفل را باز کن.'
    return
  }
  if (tryHandlePrototypePreviewClick(event, target)) return

  const currentTool = String(activeTool.value || 'select')

  if (inlineTextEditState?.element && inlineTextEditState.element !== target && !inlineTextEditState.element.contains(target)) {
    void finishInlineTextEditing(true)
  }

  if (currentTool === 'text') {
    if (inlineTextEditState?.element && (target === inlineTextEditState.element || inlineTextEditState.element.contains(target))) {
      return
    }
    event.preventDefault()
    event.stopPropagation()
    if (isInlineTextTarget(target)) {
      const nodeId = ensureVisualNodeId(target)
      if (!visualLayerIndex.value[nodeId]) upsertSingleLayerForElement(target)
      selectVisualLayer(nodeId)
      startInlineTextEditing(target, { selectAll: false })
      return
    }
    const createdId = createElementForActiveTool(event)
    if (!createdId) return
    const createdElement = getVisualElementById(createdId)
    if (createdElement) startInlineTextEditing(createdElement)
    return
  }

  if (INSERTABLE_TOOLS.has(currentTool)) {
    event.preventDefault()
    event.stopPropagation()
    createElementForActiveTool(event)
    return
  }

  // Always block native navigation/submit behavior inside preview.
  event.preventDefault()
  event.stopPropagation()

  // Throttle: ignore clicks within the window to avoid chained handlers on heavy pages.
  if (_clickThrottleTimer !== null) return
  _clickThrottleTimer = window.setTimeout(() => { _clickThrottleTimer = null }, CLICK_THROTTLE_MS)

  const anchor = target.closest('a[href]')
  if (anchor) anchor.blur()

  if (pendingSelectionFrameHandle !== null) window.cancelAnimationFrame(pendingSelectionFrameHandle)
  pendingSelectionFrameHandle = window.requestAnimationFrame(() => {
    pendingSelectionFrameHandle = null
    const nodeId = ensureVisualNodeId(target)
    if (!visualLayerIndex.value[nodeId]) upsertSingleLayerForElement(target)
    const range = Boolean(event?.shiftKey)
    const toggle = Boolean(event?.metaKey || event?.ctrlKey)
    if (!range && !toggle && visualSelectedId.value === nodeId && visualSelectedElement === target) return
    selectVisualLayer(nodeId, {
      range,
      additive: toggle,
      toggle,
      rangeIds: range ? resolveSelectionRangeIds(visualSelectedId.value, nodeId) : [],
    })
  })
}

function onVisualFrameDoubleClick(event) {
  const initialTarget = resolveEventTargetElement(event?.target)
  if (!initialTarget) return
  const target = initialTarget.closest('*')
  if (!isVisualEditableElement(target)) return
  if (isLayerLockedElement(target)) return
  if (!isInlineTextTarget(target)) return
  const active = String(activeTool.value || 'select')
  if (active !== 'select' && active !== 'text') return
  event.preventDefault()
  event.stopPropagation()
  const nodeId = ensureVisualNodeId(target)
  if (!visualLayerIndex.value[nodeId]) upsertSingleLayerForElement(target)
  selectVisualLayer(nodeId)
  startInlineTextEditing(target, { selectAll: false })
}

function onVisualFrameWheel(event) {
  if (!event) return
  const hasPrimaryModifier = Boolean(event.metaKey || event.ctrlKey)
  if (!hasPrimaryModifier) return
  event.preventDefault()
  event.stopPropagation()
  const direction = Number(event.deltaY || 0) < 0 ? 1 : -1
  zoomCanvasByStep(direction, {
    anchorClientX: Number(event.clientX || 0),
    anchorClientY: Number(event.clientY || 0),
  })
}

function onVisualFrameKeydown(event) {
  handleEditorKeydown(event, { fromFrame: true })
}

function onVisualFrameKeyup(event) {
  const code = String(event?.code || '')
  if (code === 'Space') canvasSpacePressed = false
}

function bindVisualFrameEvents(doc, previousDoc = null) {
  if (!doc) return
  if (visualFrameClickHandler && previousDoc) previousDoc.removeEventListener('click', visualFrameClickHandler, true)
  if (visualFrameDblClickHandler && previousDoc) previousDoc.removeEventListener('dblclick', visualFrameDblClickHandler, true)
  if (visualFramePointerDownHandler && previousDoc) previousDoc.removeEventListener('mousedown', visualFramePointerDownHandler, true)
  if (visualFrameWheelHandler && previousDoc) previousDoc.removeEventListener('wheel', visualFrameWheelHandler, true)
  if (visualFrameKeyDownHandler && previousDoc) previousDoc.removeEventListener('keydown', visualFrameKeyDownHandler, true)
  if (visualFrameKeyUpHandler && previousDoc) previousDoc.removeEventListener('keyup', visualFrameKeyUpHandler, true)
  if (visualFrameScrollHandler && previousDoc) previousDoc.removeEventListener('scroll', visualFrameScrollHandler, true)
  if (visualFrameMeasureMoveHandler && previousDoc) previousDoc.removeEventListener('mousemove', visualFrameMeasureMoveHandler, true)
  if (visualFrameScrollHandler && previousDoc?.defaultView) previousDoc.defaultView.removeEventListener('resize', visualFrameScrollHandler, true)
  detachFramePointerDragListeners(previousDoc)
  detachResizeDragListeners(previousDoc)
  visualFrameClickHandler = onVisualFrameClick
  visualFrameDblClickHandler = onVisualFrameDoubleClick
  visualFramePointerDownHandler = onVisualFramePointerDown
  visualFrameWheelHandler = onVisualFrameWheel
  visualFrameKeyDownHandler = onVisualFrameKeydown
  visualFrameKeyUpHandler = onVisualFrameKeyup
  visualFrameScrollHandler = () => {
    syncResizeOverlay()
    syncRedlineOverlay()
  }
  visualFrameMeasureMoveHandler = onVisualFrameMouseMove
  doc.addEventListener('click', visualFrameClickHandler, true)
  doc.addEventListener('dblclick', visualFrameDblClickHandler, true)
  doc.addEventListener('mousedown', visualFramePointerDownHandler, true)
  doc.addEventListener('wheel', visualFrameWheelHandler, { capture: true, passive: false })
  doc.addEventListener('keydown', visualFrameKeyDownHandler, true)
  doc.addEventListener('keyup', visualFrameKeyUpHandler, true)
  doc.addEventListener('scroll', visualFrameScrollHandler, true)
  doc.addEventListener('mousemove', visualFrameMeasureMoveHandler, true)
  if (doc.defaultView) doc.defaultView.addEventListener('resize', visualFrameScrollHandler, true)
  ensureResizeOverlay(doc)
  ensureGuideOverlay(doc)
  ensureMeasureOverlay(doc)
  ensureRedlineOverlay(doc)
  ensureMarqueeOverlay(doc)
  ensureCanvasDecorOverlays(doc)
  syncCanvasDecorOverlays()
  syncRedlineOverlay()
}

function applyVisualField(field, value) {
  const selectedIds = Array.isArray(visualSelectedIds.value) && visualSelectedIds.value.length
    ? [...visualSelectedIds.value]
    : (visualSelectedId.value ? [visualSelectedId.value] : [])
  if (!selectedIds.length) return
  pushVisualHistorySnapshot()
  success.value = ''
  const nextValue = String(value ?? '')

  const map = { ...visualOverridesMap.value }

  for (const nodeId of selectedIds) {
    const element = getVisualElementById(nodeId)
    const layer = visualLayerIndex.value?.[nodeId]
    if (!element || !layer) continue
    const selector = ensureLayerSelector(nodeId, element)
    if (!selector) continue

    const existing = map[selector]
      ? { ...map[selector], styles: { ...(map[selector].styles || {}) } }
      : { selector, tag: layer.tag, label: layer.label, styles: {}, apply_text: false, text_content: '', apply_html: false, html_content: '' }

    if (field === 'text_content') {
      if (nodeId === visualSelectedId.value) visualProps.value.text_content = nextValue
      element.textContent = nextValue
      existing.apply_html = false
      existing.html_content = ''
      if (nextValue === String(layer.original_text || '')) {
        existing.apply_text = false
        existing.text_content = ''
      } else {
        existing.apply_text = true
        existing.text_content = nextValue
      }
    } else {
      const styleKey = String(field || '').trim()
      if (!styleKey) continue
      if (styleKey === 'rotation') {
        const parsed = parseRotationInput(nextValue)
        if (!parsed.valid) continue
        const existingTransform = String(element.style.transform || '').trim()
        const split = splitTransformRotation(existingTransform)
        const nextTransform = parsed.empty
          ? String(split.base || '').trim()
          : `${split.base ? `${split.base} ` : ''}rotate(${parsed.deg}deg)`.trim()
        if (nodeId === visualSelectedId.value) visualProps.value.rotation = parsed.empty ? '' : `${parsed.deg}deg`
        if (nextTransform) {
          existing.styles.transform = nextTransform
          element.style.transform = nextTransform
        } else {
          delete existing.styles.transform
          element.style.transform = ''
        }
        if (nodeId === visualSelectedId.value) syncResizeOverlay()
      } else {
        if (nodeId === visualSelectedId.value) visualProps.value[styleKey] = nextValue
        if (nextValue.trim()) {
          existing.styles[styleKey] = nextValue
          if (styleKey.startsWith('--') || styleKey.includes('-')) {
            element.style.setProperty(styleKey, nextValue)
          } else {
            element.style[styleKey] = nextValue
          }
        } else {
          delete existing.styles[styleKey]
          if (styleKey.startsWith('--') || styleKey.includes('-')) {
            element.style.removeProperty(styleKey)
          } else {
            element.style[styleKey] = ''
          }
        }
      }
    }

    if (!existing.apply_text && !existing.apply_html && !Object.keys(existing.styles || {}).length) delete map[selector]
    else map[selector] = existing
  }

  visualOverridesMap.value = map
  nextTick(() => { syncResizeOverlay(); syncRedlineOverlay() })
}

function resetSelectedVisualLayer() {
  if (!visualSelectedLayer.value) return
  const selector = ensureLayerSelector(visualSelectedLayer.value.id, visualSelectedElement)
  if (!selector) return
  const map = { ...visualOverridesMap.value }
  if (map[selector]) { delete map[selector]; visualOverridesMap.value = map }
  reloadPreview()
}

function stripInlineScripts(markup) {
  return String(markup || '').replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '')
}

function stripJinjaTags(markup) {
  return String(markup || '').replace(/\{#[\s\S]*?#\}/g, '').replace(/\{%-?[\s\S]*?-?%\}/g, '').replace(/\{\{[\s\S]*?\}\}/g, '')
}

function stripStylesheetLinks(markup) {
  return String(markup || '').replace(/<link\b[^>]*rel=["']?stylesheet["']?[^>]*>/gi, '')
}

function sanitizePreviewStyleMarkup(markup) {
  return String(markup || '')
    .replace(/@import\s+(?:url\()?['"]?(?!https?:|data:|\/\/)[^'")]+['"]?\)?[^;]*;/gi, '')
}

function extractVuePreviewMarkup(source) {
  const raw = String(source || '')
  const templateMatch = raw.match(/<template\b[^>]*>([\s\S]*?)<\/template>/i)
  const templateMarkup = templateMatch ? templateMatch[1] : raw
  const styleChunks = []
  const styleRe = /<style\b[^>]*>([\s\S]*?)<\/style>/gi
  let match = null
  while ((match = styleRe.exec(raw)) !== null) styleChunks.push(String(match[1] || ''))
  return { markup: templateMarkup, styles: styleChunks.join('\n') }
}

function extractPreviewPartsFromSource() {
  const fileType = String(fileInfo.value?.file_type || '').toLowerCase()
  const source = String(sourceCode.value || '')
  let bodyMarkup = ''
  let styleMarkup = ''
  if (fileType === 'vue') {
    const vueParts = extractVuePreviewMarkup(source)
    bodyMarkup = stripStylesheetLinks(stripInlineScripts(stripJinjaTags(vueParts.markup)))
    styleMarkup = sanitizePreviewStyleMarkup(stripInlineScripts(vueParts.styles))
  } else {
    bodyMarkup = stripStylesheetLinks(stripInlineScripts(stripJinjaTags(source)))
  }
  return {
    bodyMarkup: String(bodyMarkup || ''),
    styleMarkup: String(styleMarkup || ''),
  }
}

function buildLightPreviewDocument() {
  const parts = extractPreviewPartsFromSource()
  const bodyMarkup = parts.bodyMarkup
  const styleMarkup = parts.styleMarkup
  const body = String(bodyMarkup || '').trim() || '<div style="padding:16px">محتوایی برای پیش‌نمایش پیدا نشد.</div>'
  const escapedBase = escapeAttributeValue(`${window.location.origin}/`)
  const headCore = [
    '<meta charset="utf-8" />', '<meta name="viewport" content="width=device-width, initial-scale=1" />',
    `<base href="${escapedBase}" />`, `<style>${styleMarkup}</style>`,
  ].join('')
  if (/<html[\s>]/i.test(body)) {
    const stamped = body.includes('management-preview-lite:') ? body : `${body}<!-- management-preview-lite:${Date.now()} -->`
    if (/<\/head>/i.test(stamped)) return stamped.replace(/<\/head>/i, `${headCore}</head>`)
    if (/<body[\s>]/i.test(stamped)) return stamped.replace(/<body([\s>])/i, `<head>${headCore}</head><body$1`)
  }
  return ['<!doctype html>', '<html dir="rtl">', '<head>', headCore, '</head>', `<body>${body}</body>`, `<!-- management-preview-lite:${Date.now()} -->`, '</html>'].join('')
}

function buildComponentPreviewDocument() {
  const parts = extractPreviewPartsFromSource()
  const body = String(parts.bodyMarkup || '').trim()
  const styleMarkup = String(parts.styleMarkup || '')
  const escapedBase = escapeAttributeValue(`${window.location.origin}/`)
  const scopedContent = body || `
    <div class="ve-component-empty">
      <strong>محتوایی برای رندر کامپوننت پیدا نشد.</strong>
      <small>template این فایل خالی است یا فقط با داده‌های runtime پر می‌شود.</small>
    </div>
  `
  const shellStyles = `
    :root { color-scheme: light; }
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; min-height: 100%; background: #f3f6fb; color: #111827; }
    body {
      font-family: 'Peyda', 'Inter', system-ui, -apple-system, sans-serif;
      display: flex;
      align-items: flex-start;
      justify-content: center;
      padding: 30px 20px;
    }
    .ve-component-canvas {
      width: min(1240px, 100%);
      min-height: 760px;
      background: #ffffff;
      border: 1px solid #d6e0ee;
      border-radius: 14px;
      box-shadow: 0 18px 38px rgba(16, 24, 40, 0.1);
      padding: 22px;
      overflow: auto;
    }
    .ve-component-meta {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      border-bottom: 1px dashed #d8e2f0;
      padding-bottom: 10px;
      margin-bottom: 18px;
      color: #4b5563;
      font-size: 12px;
      direction: rtl;
    }
    .ve-component-meta code {
      direction: ltr;
      color: #0f172a;
      background: #eef4fd;
      border: 1px solid #d5e5ff;
      border-radius: 999px;
      padding: 3px 10px;
      font-size: 11px;
    }
    .ve-component-empty {
      border: 1px dashed #c7d2e6;
      border-radius: 10px;
      padding: 18px;
      background: #f8fbff;
      display: grid;
      gap: 6px;
    }
    .ve-component-empty strong { font-size: 14px; color: #1f2937; }
    .ve-component-empty small { font-size: 12px; color: #6b7280; }
  `
  const componentLabel = escapeHtmlText(String(fileInfo.value?.file || fileInfo.value?.component || 'component'))
  return [
    '<!doctype html>',
    '<html dir="rtl">',
    '<head>',
    '<meta charset="utf-8" />',
    '<meta name="viewport" content="width=device-width, initial-scale=1" />',
    `<base href="${escapedBase}" />`,
    `<style>${shellStyles}</style>`,
    `<style>${styleMarkup}</style>`,
    '</head>',
    '<body>',
    '<main class="ve-component-canvas">',
    `<div class="ve-component-meta"><span>حالت کامپوننت مستقل</span><code>${componentLabel}</code></div>`,
    scopedContent,
    '</main>',
    `<!-- management-preview-component:${Date.now()} -->`,
    '</body>',
    '</html>',
  ].join('')
}

async function reloadPreview() {
  if (!hasEditorTarget.value) return
  previewInitialized.value = true
  previewLoading.value = true
  previewError.value = ''
  layerScanInProgress.value = false
  visualLayerScanToken += 1
  clearVisualSelection()
  resetVisualLayerState()
  clearPreviewTimeout()
  previewFrameLoadToken += 1
  const token = previewFrameLoadToken

  const previewScopeValue = resolvedPreviewScope.value

  if (previewScopeValue === 'component') {
    previewMode.value = 'srcdoc'
    visualPreviewSrc.value = ''
    try {
      visualPreviewSrcdoc.value = buildComponentPreviewDocument()
    } catch (err) {
      if (token === previewFrameLoadToken) {
        previewLoading.value = false
        previewError.value = err?.message || 'ساخت پیش‌نمایش کامپوننت انجام نشد.'
      }
      return
    }
    previewTimeoutHandle = window.setTimeout(() => {
      if (token !== previewFrameLoadToken) return
      previewLoading.value = false
      previewError.value = 'پیش‌نمایش کامپوننت لود نشد.'
    }, PREVIEW_TIMEOUT_MS)
    return
  }

  // Load actual rendered page via URL so Vue/Jinja templates render correctly
  const previewRoute = String(visualPreviewBaseRoute.value || route.value || '').trim()
  if (previewRoute) {
    const sep = previewRoute.includes('?') ? '&' : '?'
    previewMode.value = 'url'
    visualPreviewSrcdoc.value = ''
    visualPreviewSrc.value = previewRoute + sep + '_ve=' + Date.now()
  } else {
    // Fallback to srcdoc when only target_file is set and no route exists
    previewMode.value = 'srcdoc'
    visualPreviewSrc.value = ''
    try {
      visualPreviewSrcdoc.value = buildLightPreviewDocument()
    } catch (err) {
      if (token === previewFrameLoadToken) {
        previewLoading.value = false
        previewError.value = err?.message || 'ساخت پیش‌نمایش انجام نشد.'
      }
      return
    }
  }

  previewTimeoutHandle = window.setTimeout(() => {
    if (token !== previewFrameLoadToken) return
    previewLoading.value = false
    previewError.value = 'پیش‌نمایش لود نشد. مطمئن شو route معتبر است و صفحه بدون لاگین در دسترس باشه.'
  }, PREVIEW_TIMEOUT_MS)
}

async function requestPreviewLoad() { await reloadPreview() }

function clearPreviewTimeout() {
  if (!previewTimeoutHandle) return
  window.clearTimeout(previewTimeoutHandle)
  previewTimeoutHandle = null
}

function clearPayloadAbortController() {
  if (!payloadAbortController) return
  try { payloadAbortController.abort() } catch {}
  payloadAbortController = null
}

function isEditorRuntimeElement(element) {
  if (!element || element.nodeType !== 1) return false
  const id = String(element.id || '').trim()
  if (id.startsWith('mysite-ve-')) return true
  if (element.classList?.contains('mysite-ve-guide-label')) return true
  if (element.classList?.contains('mysite-ve-guide-line-v')) return true
  if (element.classList?.contains('mysite-ve-guide-line-h')) return true
  if (element.classList?.contains('mysite-ve-resize-handle')) return true
  if (element.classList?.contains('mysite-ve-ruler-top')) return true
  if (element.classList?.contains('mysite-ve-ruler-left')) return true
  if (element.classList?.contains('mysite-ve-guide-persistent')) return true
  if (element.closest?.('#mysite-ve-resize-overlay, #mysite-ve-guide-overlay, #mysite-ve-measure-overlay, #mysite-ve-redline-overlay, #mysite-ve-marquee, #mysite-ve-grid-overlay, #mysite-ve-layout-grid-overlay, #mysite-ve-layout-guides-layer, #mysite-ve-rulers, #mysite-ve-flow-insertion-line, #mysite-ve-text-toolbar')) return true
  return false
}

function markVisualStructureDirty() {
  if (visualStructureDirty.value) return
  visualStructureDirty.value = true
  recomputeDirtyState()
}

function disconnectVisualStructureObserver() {
  if (!visualStructureObserver) return
  try { visualStructureObserver.disconnect() } catch {}
  visualStructureObserver = null
}

function attachVisualStructureObserver(doc) {
  disconnectVisualStructureObserver()
  if (!doc?.body || typeof MutationObserver !== 'function') return
  visualStructureObserverIgnoreUntil = Date.now() + 700
  visualStructureObserver = new MutationObserver((mutations) => {
    if (Date.now() < visualStructureObserverIgnoreUntil) return
    if (visualRestoringHistory || previewLoading.value) return
    for (const mutation of mutations || []) {
      if (!mutation || mutation.type !== 'childList') continue
      const target = mutation.target
      if (target?.nodeType === 1 && isEditorRuntimeElement(target)) continue
      const added = Array.from(mutation.addedNodes || []).some((node) => node?.nodeType === 1 && !isEditorRuntimeElement(node))
      const removed = Array.from(mutation.removedNodes || []).some((node) => node?.nodeType === 1 && !isEditorRuntimeElement(node))
      if (!added && !removed) continue
      markVisualStructureDirty()
      break
    }
  })
  try {
    visualStructureObserver.observe(doc.body, { childList: true, subtree: true })
  } catch {
    disconnectVisualStructureObserver()
  }
}

function serializePersistablePreviewBodyHtml() {
  if (!visualFrameDocument?.body) return ''
  const bodyClone = visualFrameDocument.body.cloneNode(true)
  for (const row of Array.from(bodyClone.querySelectorAll('#mysite-ve-resize-overlay, #mysite-ve-guide-overlay, #mysite-ve-measure-overlay, #mysite-ve-redline-overlay, #mysite-ve-marquee, #mysite-ve-grid-overlay, #mysite-ve-layout-grid-overlay, #mysite-ve-layout-guides-layer, #mysite-ve-rulers, #mysite-ve-flow-insertion-line, #mysite-ve-text-toolbar'))) {
    row.remove()
  }
  const nodes = [bodyClone, ...Array.from(bodyClone.querySelectorAll('*'))]
  for (const node of nodes) {
    if (!node || node.nodeType !== 1) continue
    node.removeAttribute(VISUAL_NODE_ATTR)
    node.removeAttribute('data-mysite-inline-text')
    node.removeAttribute(LAYER_PREV_DISPLAY_ATTR)
    node.removeAttribute('data-mysite-prototype-frame')
    if (node.hasAttribute('contenteditable')) node.removeAttribute('contenteditable')
    node.classList?.remove?.('mysite-ve-inline-text-editing')
  }
  return String(bodyClone.innerHTML || '').trim()
}

function mergePreviewBodyIntoSource(sourceText, bodyMarkup, fileType = '') {
  const source = String(sourceText || '')
  const body = String(bodyMarkup || '').trim()
  const type = String(fileType || '').trim().toLowerCase()
  if (!body) return source
  if (!source.trim()) return type === 'html' ? body : source
  if (type === 'vue' && /<template\b[^>]*>[\s\S]*<\/template>/i.test(source)) {
    return source.replace(/<template\b([^>]*)>[\s\S]*?<\/template>/i, `<template$1>\n${body}\n</template>`)
  }
  if (/<body\b[^>]*>[\s\S]*<\/body>/i.test(source)) {
    return source.replace(/<body\b([^>]*)>[\s\S]*?<\/body>/i, `<body$1>\n${body}\n</body>`)
  }
  if (type === 'html') return body
  return source
}

function buildPersistableFullSourceFromPreview() {
  if (!visualStructureDirty.value) return ''
  const bodyMarkup = serializePersistablePreviewBodyHtml()
  if (!bodyMarkup) return ''
  const fileType = String(fileInfo.value?.file_type || '').trim().toLowerCase()
  return mergePreviewBodyIntoSource(sourceCode.value, bodyMarkup, fileType)
}

function buildVisualSaveItems() {
  return Object.values(visualOverridesMap.value || {}).map((row) => ({
    selector: row.selector,
    tag: row.tag || '',
    label: row.label || '',
    styles: row.styles || {},
    apply_text: Boolean(row.apply_text),
    text_content: row.apply_text ? String(row.text_content ?? '') : '',
    enabled: true,
    apply_html: Boolean(row.apply_html),
    html_content: row.apply_html ? String(row.html_content ?? '') : '',
  }))
}

function ensureBodyStructureOverrideForCurrentPreview() {
  const bodyMarkup = serializePersistablePreviewBodyHtml()
  if (!bodyMarkup) return false
  const selector = 'body'
  const map = { ...(visualOverridesMap.value || {}) }
  const existing = map[selector]
  if (
    existing &&
    existing.apply_html &&
    !existing.apply_text &&
    String(existing.html_content || '') === bodyMarkup
  ) return false
  map[selector] = {
    selector,
    tag: 'body',
    label: 'Body Snapshot',
    styles: existing?.styles && typeof existing.styles === 'object' ? { ...existing.styles } : {},
    apply_text: false,
    text_content: '',
    apply_html: true,
    html_content: bodyMarkup,
  }
  visualOverridesMap.value = map
  return true
}

async function onVisualFrameLoad() {
  clearPreviewTimeout()
  const loadToken = previewFrameLoadToken
  try {
    const iframe = visualPreviewFrame.value
    if (!iframe) throw new Error('iframe پیش‌نمایش پیدا نشد.')

    const iframeWin = iframe.contentWindow
    const doc = iframe.contentDocument || iframeWin?.document
    if (!doc) throw new Error('document پیش‌نمایش در دسترس نیست.')

    // If page redirected to login or is cross-origin, body may be inaccessible
    let bodyAccessible = false
    try { bodyAccessible = Boolean(doc.body) } catch { bodyAccessible = false }
    if (!bodyAccessible) {
      throw new Error('صفحه در iframe قابل دسترس نیست. احتمالاً نیاز به لاگین دارد یا cross-origin است.')
    }

    previewError.value = ''
    const previousFrameDoc = visualFrameDocument
    disconnectVisualStructureObserver()
    visualFrameDocument = doc

    if (previousFrameDoc && visualFrameAnchorBlockHandler) {
      previousFrameDoc.removeEventListener('click', visualFrameAnchorBlockHandler, true)
    }
    if (previousFrameDoc && visualFrameSubmitBlockHandler) {
      previousFrameDoc.removeEventListener('submit', visualFrameSubmitBlockHandler, true)
    }

    // Inject editor UI styles
    injectVisualEditorStyles(doc)
    applyCanvasZoomToDocument(doc)

    // Block all link navigations inside the iframe so we don't lose the preview
    blockIframeNavigation(doc, iframeWin)

    // Re-bind click handler for element selection
    bindVisualFrameEvents(doc, previousFrameDoc)

    // Apply any saved overrides and raw CSS
    applyVisualOverridesToDocument(doc)
    applyRawCssToDocument(doc)
    applyActiveTokenModeToDocument(doc)
    applyPrototypeModelToDocument(doc)
    focusPrototypeStartFrame(doc)
    collectPreviewCssVariables(doc)

    clearVisualSelection()
    resetVisualLayerState()
    visualUndoStack = []
    visualRedoStack = []
    hideSmartGuides()
    hideFlowInsertionLine()
    hideMeasureOverlay()
    hideRedlineOverlay()
    hideMarqueeOverlay()
    hideTextToolbar()
    suppressFrameClickOnce = false
    syncCanvasDecorOverlays()
    syncRedlineOverlay()
    attachVisualStructureObserver(doc)
    visualStructureDirty.value = false

    if (loadToken === previewFrameLoadToken) previewLoading.value = false

    // Auto-scan layers after a short delay to let the page's own scripts finish
    window.setTimeout(async () => {
      if (loadToken !== previewFrameLoadToken) return
      await runVisualLayerScan(doc, { loadToken })
      focusPrototypeStartFrame(doc)
      pushVisualHistorySnapshot({ force: true, clearRedo: true })
    }, 400)

    // Some pages mount dynamic nodes slightly later. Run one more scan to keep Layers complete.
    window.setTimeout(async () => {
      if (loadToken !== previewFrameLoadToken) return
      await runVisualLayerScan(doc, { loadToken })
    }, 1700)

    success.value = 'پیش‌نمایش بارگذاری شد. روی هر المنت کلیک کن تا انتخاب و ادیت بشه.'
  } catch (err) {
    if (loadToken === previewFrameLoadToken) {
      previewError.value = err?.message || 'در پردازش پیش‌نمایش خطا رخ داد.'
    }
  } finally {
    if (loadToken === previewFrameLoadToken) previewLoading.value = false
  }
}

// Prevent iframe links from navigating away from the preview
function blockIframeNavigation(doc, iframeWin) {
  if (!doc) return
  if (visualFrameAnchorBlockHandler) doc.removeEventListener('click', visualFrameAnchorBlockHandler, true)
  if (visualFrameSubmitBlockHandler) doc.removeEventListener('submit', visualFrameSubmitBlockHandler, true)

  visualFrameAnchorBlockHandler = (event) => {
    const initialTarget = resolveEventTargetElement(event?.target)
    const anchor = initialTarget?.closest?.('a[href]')
    if (!anchor) return
    event.preventDefault()
  }
  visualFrameSubmitBlockHandler = (event) => {
    event.preventDefault()
    event.stopPropagation()
  }
  doc.addEventListener('click', visualFrameAnchorBlockHandler, true)
  doc.addEventListener('submit', visualFrameSubmitBlockHandler, true)

  try {
    if (iframeWin) {
      // Prevent SPA route changes inside preview.
      if (!iframeWin.__mysite_visual_history_blocked__) {
        iframeWin.__mysite_visual_history_blocked__ = true
        const blocked = () => undefined
        if (iframeWin.history?.pushState) iframeWin.history.pushState = blocked
        if (iframeWin.history?.replaceState) iframeWin.history.replaceState = blocked
        if (typeof iframeWin.open === 'function') iframeWin.open = () => null
      }
    }
  } catch { /* cross-origin guard */ }
}

async function loadEditorPayload() {
  const hasRoute = Boolean(String(route.value || '').trim())
  const hasTargetFile = Boolean(String(selectedTargetFile.value || '').trim())
  if (!hasRoute && !hasTargetFile) { loading.value = false; return }
  cancelAutoSave()
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const params = new URLSearchParams()
    if (hasRoute) params.set('route', route.value)
    if (hasTargetFile) params.set('target_file', selectedTargetFile.value)
    const endpoint = `/api/method/mysite.api.get_management_visual_editor_payload?${params.toString()}`
    let response, payload
    try {
      const timed = await fetchJsonWithTimeout(endpoint, { credentials: 'same-origin' }, PAYLOAD_TIMEOUT_MS)
      response = timed.response; payload = timed.payload
    } catch (timedError) {
      if (timedError?.name !== 'AbortError') throw timedError
      const fallback = await fetchJsonWithTimeout(endpoint, { credentials: 'same-origin' }, 15000)
      response = fallback.response; payload = fallback.payload
    }
    if (!response.ok || payload.exception || payload.exc_type) throw new Error(payload?.message || 'دریافت اطلاعات ادیتور با خطا مواجه شد.')
    const result = payload.message || payload
    const nextRoute = normalizeEditorRoute(result.route || route.value || '')
    route.value = nextRoute
    fileInfo.value = { file: result.file || '', file_type: result.file_type || '', component: result.component || '' }
    editableFiles.value = Array.isArray(result.editable_files) ? result.editable_files : []
    selectedTargetFile.value = result.file || selectedTargetFile.value || ''
    isComponentFile.value = Boolean(result.is_component_file)
    componentUsageRoutes.value = (Array.isArray(result.component_usage_routes) ? result.component_usage_routes : [])
      .map((routeValue) => normalizeEditorRoute(routeValue))
      .filter(Boolean)
    activeBranch.value = String(result.active_branch || DEFAULT_EDITOR_BRANCH).trim() || DEFAULT_EDITOR_BRANCH
    versioningBranches.value = Array.isArray(result.versioning_branches) ? result.versioning_branches : []
    componentLibrarySummaries.value = Array.isArray(result.component_library_summaries) ? result.component_library_summaries : []
    if (!componentLibrarySummaries.value.some((row) => String(row?.name || '') === String(activeLibraryName.value || ''))) {
      activeLibraryName.value = String(componentLibrarySummaries.value[0]?.name || 'global').trim() || 'global'
    }
    prototypeModel.value = normalizePrototypeModel(result.prototype_model)
    const nextMap = {}
    for (const row of Array.isArray(result.visual_overrides) ? result.visual_overrides : []) {
      const normalized = normalizeVisualOverrideItem(row)
      if (!normalized) continue
      nextMap[normalized.selector] = normalized
    }
    visualOverridesMap.value = nextMap
    rawCss.value = String(result.visual_raw_css || '')
    sourceCode.value = String(result.source || '')
    {
      const selection = resolveActiveTokenSelection(
        result.token_collections,
        String(result.token_active_collection || ''),
        String(result.token_active_mode || 'light')
      )
      tokenCollections.value = selection.collections
      activeTokenCollectionId.value = selection.collectionId
      activeTokenMode.value = selection.mode
    }
    historyVersions.value = Array.isArray(result.history) ? result.history : []
    visualPreviewBaseRoute.value = normalizeEditorRoute(result.preview_route || nextRoute || '')
    previewInitialized.value = false
    previewLoading.value = false
    previewError.value = ''
    previewMode.value = 'url'
    visualPreviewSrc.value = ''
    visualPreviewSrcdoc.value = ''
    clearVisualSelection()
    visualUndoStack = []
    visualRedoStack = []
    visualClipboardHtml = ''
    syncPrototypeDraftFromSelection()
    setDirtyBaselineFromCurrentState()
    maybeRestoreCrashRecoverySnapshot()
  } catch (err) {
    error.value = err?.name === 'AbortError' ? 'زمان پاسخ ادیتور طولانی شد.' : (err?.message || 'خطا در دریافت اطلاعات ادیتور.')
  } finally {
    loading.value = false
  }
}

async function onTargetFileChange() {
  if (!selectedTargetFile.value) return
  if (!confirmDiscardChanges()) { selectedTargetFile.value = fileInfo.value.file || ''; return }
  const hadPreview = previewInitialized.value
  const params = new URLSearchParams(window.location.search)
  if (route.value) params.set('route', route.value); else params.delete('route')
  params.set('target_file', selectedTargetFile.value)
  window.history.replaceState({}, '', `${window.location.pathname}?${params.toString()}`)
  await loadEditorPayload()
  if (hadPreview) await requestPreviewLoad()
}

async function saveVisualChanges(options = {}) {
  if (!route.value && !selectedTargetFile.value) return false
  const skipReload = options?.skipReload === undefined ? true : Boolean(options?.skipReload)
  const silentSuccess = Boolean(options?.silentSuccess)
  const persistStructure = options?.persistStructure === undefined
    ? Boolean(visualStructureDirty.value)
    : Boolean(options?.persistStructure)
  clearAutoSaveTimer()
  savingVisual.value = true
  error.value = ''
  if (!silentSuccess) success.value = ''
  let saved = false
  try {
    const fullSourceForSave = persistStructure ? buildPersistableFullSourceFromPreview() : ''
    if (fullSourceForSave) sourceCode.value = fullSourceForSave
    const items = buildVisualSaveItems()
    const requestBody = {
      route: route.value || '',
      target_file: selectedTargetFile.value || '',
      active_branch: activeBranch.value || DEFAULT_EDITOR_BRANCH,
      items,
      raw_css: rawCss.value,
      token_collections: cloneTokenCollections(tokenCollections.value),
      token_active_collection: String(activeTokenCollectionId.value || ''),
      token_active_mode: String(activeTokenMode.value || 'light'),
      prototype_model: normalizePrototypeModel(prototypeModel.value),
      note: saveNote.value,
    }
    if (fullSourceForSave) requestBody.full_source = fullSourceForSave
    let { response, payload } = await postEditorMethodWithFallback('/api/method/mysite.api.save_management_visual_editor_changes', requestBody)
    if (!response.ok || payload.exception || payload.exc_type) throw new Error(payload?.message || 'ذخیره با خطا مواجه شد.')
    const workflowEnforced = Boolean(payload?.workflow_enforced)
    if (workflowEnforced) {
      const state = String(payload?.state || 'Draft')
      throw new Error(payload?.message || `تغییرات برای تایید ثبت شد (State: ${state}) و هنوز منتشر نشده است.`)
    }

    let sourceChanged = Boolean(payload?.source_changed)
    let usedBodyFallback = false
    if (persistStructure && !sourceChanged) {
      usedBodyFallback = ensureBodyStructureOverrideForCurrentPreview()
      if (usedBodyFallback) {
        const retryBody = {
          ...requestBody,
          items: buildVisualSaveItems(),
        }
        delete retryBody.full_source
        const retry = await postEditorMethodWithFallback('/api/method/mysite.api.save_management_visual_editor_changes', retryBody)
        response = retry.response
        payload = retry.payload
        if (!response.ok || payload.exception || payload.exc_type) throw new Error(payload?.message || 'ذخیره fallback ساختار با خطا مواجه شد.')
        if (Boolean(payload?.workflow_enforced)) {
          const state = String(payload?.state || 'Draft')
          throw new Error(payload?.message || `تغییرات fallback برای تایید ثبت شد (State: ${state}) و هنوز منتشر نشده است.`)
        }
        sourceChanged = Boolean(payload?.source_changed)
      }
    }

    if (!silentSuccess) {
      if (fullSourceForSave && sourceChanged) success.value = 'تغییرات بصری و ساختاری ذخیره شد.'
      else if (usedBodyFallback) success.value = 'تغییرات ساختاری به‌صورت Visual Snapshot ذخیره شد.'
      else success.value = 'تغییرات CSS و تنظیمات بصری ذخیره شد.'
    }
    if (skipReload) {
      setDirtyBaselineFromCurrentState()
    } else {
      await loadEditorPayload()
    }
    saved = true
  } catch (err) {
    error.value = err?.message || 'خطا در ذخیره تغییرات.'
  } finally {
    savingVisual.value = false
  }
  return saved
}

async function saveSourceCode(options = {}) {
  if (!route.value && !selectedTargetFile.value) return false
  const skipReload = options?.skipReload === undefined ? true : Boolean(options?.skipReload)
  const silentSuccess = Boolean(options?.silentSuccess)
  clearAutoSaveTimer()
  savingSource.value = true
  error.value = ''
  if (!silentSuccess) success.value = ''
  let saved = false
  try {
    const { response, payload } = await postEditorMethodWithFallback('/api/method/mysite.api.save_management_visual_editor_changes', {
      route: route.value || '',
      target_file: selectedTargetFile.value || '',
      active_branch: activeBranch.value || DEFAULT_EDITOR_BRANCH,
      full_source: sourceCode.value,
      token_collections: cloneTokenCollections(tokenCollections.value),
      token_active_collection: String(activeTokenCollectionId.value || ''),
      token_active_mode: String(activeTokenMode.value || 'light'),
      prototype_model: normalizePrototypeModel(prototypeModel.value),
      note: saveNote.value || 'manual-source-edit',
    })
    if (!response.ok || payload.exception || payload.exc_type) throw new Error(payload?.message || 'ذخیره مستقیم فایل با خطا مواجه شد.')
    if (Boolean(payload?.workflow_enforced)) {
      const state = String(payload?.state || 'Draft')
      throw new Error(payload?.message || `تغییرات برای تایید ثبت شد (State: ${state}) و هنوز منتشر نشده است.`)
    }
    if (!silentSuccess) success.value = 'فایل با موفقیت ذخیره شد.'
    if (skipReload) {
      setDirtyBaselineFromCurrentState()
    } else {
      await loadEditorPayload()
    }
    saved = true
  } catch (err) {
    error.value = err?.message || 'خطا در ذخیره فایل.'
  } finally {
    savingSource.value = false
  }
  return saved
}

async function restoreVersion(versionId) {
  if ((!route.value && !selectedTargetFile.value) || !versionId) return
  cancelAutoSave()
  restoringVersionId.value = versionId
  error.value = ''
  success.value = ''
  try {
    const response = await fetch('/api/method/mysite.api.restore_management_visual_editor_history', {
      method: 'POST', credentials: 'same-origin',
      headers: buildApiJsonHeaders(),
      body: JSON.stringify({ route: route.value || '', target_file: selectedTargetFile.value || '', version_id: versionId }),
    })
    const payload = await parseJsonResponse(response)
    if (!response.ok || payload.exception || payload.exc_type) throw new Error(payload?.message || 'بازگردانی نسخه با خطا مواجه شد.')
    success.value = 'نسخه انتخابی با موفقیت بازگردانی شد.'
    await loadEditorPayload()
  } catch (err) {
    error.value = err?.message || 'خطا در بازگردانی نسخه.'
  } finally {
    restoringVersionId.value = ''
  }
}

async function setActiveBranch(branchName) {
  const nextBranch = String(branchName || '').trim()
  if (!nextBranch || nextBranch === activeBranch.value) return false
  if (!confirmDiscardChanges()) return false
  const hadPreview = previewInitialized.value
  error.value = ''
  try {
    const { response, payload } = await postEditorMethodWithFallback('/api/method/mysite.api.set_management_visual_editor_active_branch', {
      route: route.value || '',
      target_file: selectedTargetFile.value || '',
      branch_name: nextBranch,
    })
    if (!response.ok || payload.exception || payload.exc_type) throw new Error(payload?.message || 'تعویض branch با خطا مواجه شد.')
    const result = payload.message || payload
    activeBranch.value = String(result?.active_branch || nextBranch).trim() || nextBranch
    versioningBranches.value = Array.isArray(result?.branches) ? result.branches : versioningBranches.value
    await loadEditorPayload()
    if (hadPreview) await requestPreviewLoad()
    success.value = `Branch فعال روی "${activeBranch.value}" قرار گرفت.`
    return true
  } catch (err) {
    error.value = err?.message || 'خطا در تغییر branch.'
    return false
  }
}

async function createVersionBranch() {
  if (!confirmDiscardChanges()) return false
  const branchNameRaw = window.prompt('نام branch جدید را وارد کن:', '')
  const branchName = normalizeBranchName(branchNameRaw)
  if (!branchName) return false
  const fromBranch = String(activeBranch.value || DEFAULT_EDITOR_BRANCH).trim() || DEFAULT_EDITOR_BRANCH
  const hadPreview = previewInitialized.value
  error.value = ''
  try {
    const { response, payload } = await postEditorMethodWithFallback('/api/method/mysite.api.create_management_visual_editor_branch', {
      route: route.value || '',
      target_file: selectedTargetFile.value || '',
      branch_name: branchName,
      from_branch: fromBranch,
    })
    if (!response.ok || payload.exception || payload.exc_type) throw new Error(payload?.message || 'ساخت branch با خطا مواجه شد.')
    const result = payload.message || payload
    activeBranch.value = String(result?.active_branch || branchName).trim() || branchName
    versioningBranches.value = Array.isArray(result?.branches) ? result.branches : versioningBranches.value
    await loadEditorPayload()
    if (hadPreview) await requestPreviewLoad()
    success.value = `Branch "${activeBranch.value}" ایجاد شد.`
    return true
  } catch (err) {
    error.value = err?.message || 'خطا در ایجاد branch.'
    return false
  }
}

async function createVersionMilestone() {
  const title = String(window.prompt('عنوان milestone:', '') || '').trim()
  if (!title) return false
  const note = String(window.prompt('توضیح milestone (اختیاری):', '') || '').trim()
  error.value = ''
  try {
    const { response, payload } = await postEditorMethodWithFallback('/api/method/mysite.api.create_management_visual_editor_milestone', {
      route: route.value || '',
      target_file: selectedTargetFile.value || '',
      branch_name: activeBranch.value || DEFAULT_EDITOR_BRANCH,
      title,
      note,
    })
    if (!response.ok || payload.exception || payload.exc_type) throw new Error(payload?.message || 'ایجاد milestone با خطا مواجه شد.')
    const result = payload.message || payload
    versioningBranches.value = Array.isArray(result?.branches) ? result.branches : versioningBranches.value
    success.value = `Milestone "${title}" ثبت شد.`
    return true
  } catch (err) {
    error.value = err?.message || 'خطا در ایجاد milestone.'
    return false
  }
}

async function mergeVersionBranch() {
  if (!confirmDiscardChanges()) return false
  const sourceDefault = String(activeBranch.value || DEFAULT_EDITOR_BRANCH).trim() || DEFAULT_EDITOR_BRANCH
  const sourceBranch = String(window.prompt('source branch:', sourceDefault) || '').trim()
  if (!sourceBranch) return false
  const targetBranch = String(window.prompt('target branch:', DEFAULT_EDITOR_BRANCH) || '').trim() || DEFAULT_EDITOR_BRANCH
  if (!targetBranch || sourceBranch === targetBranch) return false
  const hadPreview = previewInitialized.value
  error.value = ''
  try {
    const { response, payload } = await postEditorMethodWithFallback('/api/method/mysite.api.merge_management_visual_editor_branch', {
      route: route.value || '',
      target_file: selectedTargetFile.value || '',
      source_branch: sourceBranch,
      target_branch: targetBranch,
      note: `manual-merge:${sourceBranch}->${targetBranch}`,
    })
    if (!response.ok || payload.exception || payload.exc_type) throw new Error(payload?.message || 'Merge branch با خطا مواجه شد.')
    const result = payload.message || payload
    activeBranch.value = String(result?.active_branch || targetBranch).trim() || targetBranch
    versioningBranches.value = Array.isArray(result?.branches) ? result.branches : versioningBranches.value
    await loadEditorPayload()
    if (hadPreview) await requestPreviewLoad()
    success.value = `Merge انجام شد: ${sourceBranch} -> ${targetBranch}.`
    return true
  } catch (err) {
    error.value = err?.message || 'خطا در merge branch.'
    return false
  }
}

async function reloadAll() {
  if (!confirmDiscardChanges()) return
  cancelAutoSave()
  const hadPreview = previewInitialized.value
  await loadEditorPayload()
  if (hadPreview) await requestPreviewLoad()
}

// ⚡ PERFORMANCE FIX: No deep watch. visualOverridesMap is shallowRef so top-level
// assignments trigger this. rawCss and sourceCode are normal refs.
watch(visualOverridesMap, () => recomputeDirtyState())
watch(rawCss, () => {
  recomputeDirtyState()
  if (visualFrameDocument) {
    applyRawCssToDocument(visualFrameDocument)
    collectPreviewCssVariables(visualFrameDocument)
  }
})
watch(sourceCode, () => recomputeDirtyState())
watch(mode, (nextMode) => {
  if (String(nextMode || 'design') !== 'developer') {
    hideMeasureOverlay()
    hideRedlineOverlay()
    return
  }
  syncRedlineOverlay()
})
watch([visualSelectedId, visualSelectedIds], () => {
  syncRedlineOverlay()
})
watch([route, selectedTargetFile, activeBranch], () => {
  crashRecoveryPromptedSessionKey = ''
})
watch(viewportPreset, (nextPreset) => {
  try {
    window.localStorage.setItem(VIEWPORT_PRESET_STORAGE_KEY, normalizeViewportPreset(nextPreset))
  } catch {
    // noop
  }
})
watch(styleSectionOpen, (nextValue) => {
  try {
    const payload = nextValue && typeof nextValue === 'object' ? nextValue : {}
    window.localStorage.setItem(STYLE_SECTION_STORAGE_KEY, JSON.stringify(payload))
  } catch {
    // noop
  }
}, { deep: true })
watch(canvasZoom, (nextValue) => {
  const zoom = clampCanvasZoom(nextValue)
  if (zoom !== nextValue) {
    canvasZoom.value = zoom
    return
  }
  try { window.localStorage.setItem(CANVAS_ZOOM_STORAGE_KEY, String(Math.round(zoom * 100))) } catch { /* noop */ }
  if (visualFrameDocument?.documentElement) applyCanvasZoomToDocument(visualFrameDocument)
})
watch(nudgeStep, (nextValue) => {
  try { window.localStorage.setItem(NUDGE_STEP_STORAGE_KEY, String(Math.max(1, Number(nextValue || 1)))) } catch { /* noop */ }
})
watch(nudgeStepLarge, (nextValue) => {
  try { window.localStorage.setItem(NUDGE_STEP_LARGE_STORAGE_KEY, String(Math.max(1, Number(nextValue || 10)))) } catch { /* noop */ }
})
watch(gridSize, (nextValue) => {
  try { window.localStorage.setItem(GRID_SIZE_STORAGE_KEY, String(Math.max(2, Number(nextValue || 8)))) } catch { /* noop */ }
  syncCanvasDecorOverlays()
})
watch(layoutGridColumns, (nextValue) => {
  try { window.localStorage.setItem(GRID_COLUMNS_STORAGE_KEY, String(Math.max(1, Number(nextValue || 12)))) } catch { /* noop */ }
  syncCanvasDecorOverlays()
})
watch(showRulers, (nextValue) => {
  try { window.localStorage.setItem(RULERS_STORAGE_KEY, nextValue ? '1' : '0') } catch { /* noop */ }
  syncCanvasDecorOverlays()
})
watch(showPixelGrid, (nextValue) => {
  try { window.localStorage.setItem(PIXEL_GRID_STORAGE_KEY, nextValue ? '1' : '0') } catch { /* noop */ }
  syncCanvasDecorOverlays()
})
watch(showLayoutGrid, (nextValue) => {
  try { window.localStorage.setItem(LAYOUT_GRID_STORAGE_KEY, nextValue ? '1' : '0') } catch { /* noop */ }
  syncCanvasDecorOverlays()
})
watch(showLayoutGuides, (nextValue) => {
  try { window.localStorage.setItem(LAYOUT_GUIDES_STORAGE_KEY, nextValue ? '1' : '0') } catch { /* noop */ }
  syncCanvasDecorOverlays()
})
watch(layoutGuideItems, (nextValue) => {
  try { window.localStorage.setItem(LAYOUT_GUIDE_ITEMS_STORAGE_KEY, JSON.stringify(normalizeGuideItems(nextValue))) } catch { /* noop */ }
  renderPersistentGuideLines(visualFrameDocument)
  syncCanvasDecorOverlays()
})
watch(componentLibrary, (nextLibrary) => {
  persistComponentLibraryToStorage(nextLibrary)
}, { deep: true })
watch(sharedTextStyles, (nextStyles) => {
  persistSharedTextStylesToStorage(nextStyles)
}, { deep: true })
watch(tokenCollections, () => {
  persistTokenStateToStorage()
  recomputeDirtyState()
  applyActiveTokenModeToDocument(visualFrameDocument)
  collectPreviewCssVariables(visualFrameDocument)
}, { deep: true })
watch(prototypeModel, () => {
  recomputeDirtyState()
  applyPrototypeModelToDocument(visualFrameDocument)
  syncPrototypeDraftFromSelection()
}, { deep: true })
watch([activeTokenCollectionId, activeTokenMode], ([nextCollectionId, nextMode], [prevCollectionId, prevMode]) => {
  if (nextCollectionId === prevCollectionId && nextMode === prevMode) return
  const selection = resolveActiveTokenSelection(tokenCollections.value, nextCollectionId, nextMode)
  tokenCollections.value = selection.collections
  if (selection.collectionId !== nextCollectionId) activeTokenCollectionId.value = selection.collectionId
  if (selection.mode !== nextMode) activeTokenMode.value = selection.mode
  persistTokenStateToStorage()
  recomputeDirtyState()
  applyActiveTokenModeToDocument(visualFrameDocument)
  collectPreviewCssVariables(visualFrameDocument)
})
watch(selectedComponentVariant, (nextVariant) => {
  if (!nextVariant) return
  componentVariantDraft.value = String(nextVariant)
})
watch(selectedComponentId, (nextId) => {
  const id = String(nextId || '').trim()
  if (!id) {
    componentSwapTarget.value = ''
    return
  }
  if (componentSwapTarget.value === id) componentSwapTarget.value = ''
})
watch([visualDirty, sourceDirty], ([nextVisualDirty, nextSourceDirty]) => {
  if (!autoSaveEnabled.value) return
  if (nextVisualDirty || nextSourceDirty) {
    scheduleAutoSave(AUTO_SAVE_DEBOUNCE_MS)
    return
  }
  if (!autoSaveRunning.value) {
    cancelAutoSave()
    autoSaveRetryCount = 0
  }
})
watch([loading, savingVisual, savingSource, restoringVersionId], () => {
  if (!autoSaveEnabled.value) return
  if (!hasUnsavedChanges()) return
  if (canAutoSave()) scheduleAutoSave(700)
})

onMounted(async () => {
  parseRouteFromQuery()
  visualPreviewBaseRoute.value = normalizeEditorRoute(route.value)
  componentLibrary.value = readComponentLibraryFromStorage()
  sharedTextStyles.value = readSharedTextStylesFromStorage()
  {
    const tokenState = readTokenStateFromStorage()
    if (tokenState) {
      tokenCollections.value = tokenState.collections
      activeTokenCollectionId.value = tokenState.activeCollectionId
      activeTokenMode.value = tokenState.activeMode
    } else {
      const selection = resolveActiveTokenSelection(defaultTokenCollections(), 'core', 'light')
      tokenCollections.value = selection.collections
      activeTokenCollectionId.value = selection.collectionId
      activeTokenMode.value = selection.mode
    }
  }
  try { setViewportPreset(window.localStorage.getItem(VIEWPORT_PRESET_STORAGE_KEY)) } catch { setViewportPreset('desktop') }
  nudgeStep.value = readNumberStorage(NUDGE_STEP_STORAGE_KEY, 1, 1, 200)
  nudgeStepLarge.value = readNumberStorage(NUDGE_STEP_LARGE_STORAGE_KEY, 10, 1, 400)
  canvasZoom.value = clampCanvasZoom(readNumberStorage(CANVAS_ZOOM_STORAGE_KEY, 100, 25, 300) / 100)
  gridSize.value = readNumberStorage(GRID_SIZE_STORAGE_KEY, 8, 2, 256)
  layoutGridColumns.value = readNumberStorage(GRID_COLUMNS_STORAGE_KEY, 12, 1, 32)
  showRulers.value = readBooleanStorage(RULERS_STORAGE_KEY, true)
  showPixelGrid.value = readBooleanStorage(PIXEL_GRID_STORAGE_KEY, false)
  showLayoutGrid.value = readBooleanStorage(LAYOUT_GRID_STORAGE_KEY, false)
  showLayoutGuides.value = readBooleanStorage(LAYOUT_GUIDES_STORAGE_KEY, true)
  try {
    const raw = window.localStorage.getItem(LAYOUT_GUIDE_ITEMS_STORAGE_KEY)
    layoutGuideItems.value = normalizeGuideItems(raw ? JSON.parse(raw) : [])
  } catch {
    layoutGuideItems.value = []
  }
  window.addEventListener('beforeunload', handleBeforeUnload)
  window.addEventListener('keydown', handleGlobalKeydown)
  window.addEventListener('keyup', handleGlobalKeyup)
  await refreshImageAssetLibrary({ silentError: true })
  await loadEditorPayload()
  if (!Object.keys(componentLibrary.value || {}).length && componentLibrarySummaries.value.length) {
    await consumeComponentLibraryFromServer({ libraryName: activeLibraryName.value, silent: true })
  }
})

onBeforeUnmount(() => {
  void finishInlineTextEditing(false)
  if (crashRecoveryPersistTimer !== null) {
    window.clearTimeout(crashRecoveryPersistTimer)
    crashRecoveryPersistTimer = null
  }
  persistCrashRecoverySnapshotNow()
  terminateLayerScanWorker()
  disconnectVisualStructureObserver()
  window.removeEventListener('beforeunload', handleBeforeUnload)
  window.removeEventListener('keydown', handleGlobalKeydown)
  window.removeEventListener('keyup', handleGlobalKeyup)
  if (visualFrameClickHandler && visualFrameDocument) visualFrameDocument.removeEventListener('click', visualFrameClickHandler, true)
  if (visualFrameDblClickHandler && visualFrameDocument) visualFrameDocument.removeEventListener('dblclick', visualFrameDblClickHandler, true)
  if (visualFramePointerDownHandler && visualFrameDocument) visualFrameDocument.removeEventListener('mousedown', visualFramePointerDownHandler, true)
  if (visualFrameWheelHandler && visualFrameDocument) visualFrameDocument.removeEventListener('wheel', visualFrameWheelHandler, true)
  if (visualFrameKeyDownHandler && visualFrameDocument) visualFrameDocument.removeEventListener('keydown', visualFrameKeyDownHandler, true)
  if (visualFrameKeyUpHandler && visualFrameDocument) visualFrameDocument.removeEventListener('keyup', visualFrameKeyUpHandler, true)
  if (visualFrameScrollHandler && visualFrameDocument) visualFrameDocument.removeEventListener('scroll', visualFrameScrollHandler, true)
  if (visualFrameMeasureMoveHandler && visualFrameDocument) visualFrameDocument.removeEventListener('mousemove', visualFrameMeasureMoveHandler, true)
  if (visualFrameScrollHandler && visualFrameDocument?.defaultView) visualFrameDocument.defaultView.removeEventListener('resize', visualFrameScrollHandler, true)
  if (visualFrameAnchorBlockHandler && visualFrameDocument) visualFrameDocument.removeEventListener('click', visualFrameAnchorBlockHandler, true)
  if (visualFrameSubmitBlockHandler && visualFrameDocument) visualFrameDocument.removeEventListener('submit', visualFrameSubmitBlockHandler, true)
  if (visualMarqueeMoveHandler && visualFrameDocument) visualFrameDocument.removeEventListener('mousemove', visualMarqueeMoveHandler, true)
  if (visualMarqueeUpHandler && visualFrameDocument) visualFrameDocument.removeEventListener('mouseup', visualMarqueeUpHandler, true)
  if (visualGuideDragMoveHandler && visualFrameDocument) visualFrameDocument.removeEventListener('mousemove', visualGuideDragMoveHandler, true)
  if (visualGuideDragUpHandler && visualFrameDocument) visualFrameDocument.removeEventListener('mouseup', visualGuideDragUpHandler, true)
  detachFramePointerDragListeners(visualFrameDocument)
  detachCanvasPanListeners(visualFrameDocument)
  detachResizeDragListeners(visualFrameDocument)
  visualFrameClickHandler = null
  visualFrameDblClickHandler = null
  visualFramePointerDownHandler = null
  visualFrameWheelHandler = null
  visualFrameKeyDownHandler = null
  visualFrameKeyUpHandler = null
  visualFrameScrollHandler = null
  visualFrameMeasureMoveHandler = null
  visualFrameAnchorBlockHandler = null
  visualFrameSubmitBlockHandler = null
  if (visualResizeOverlay?.parentElement) visualResizeOverlay.parentElement.removeChild(visualResizeOverlay)
  visualResizeOverlay = null
  if (visualGuideOverlay?.parentElement) visualGuideOverlay.parentElement.removeChild(visualGuideOverlay)
  visualGuideOverlay = null
  visualGuideV = null
  visualGuideH = null
  if (visualMeasureOverlay?.parentElement) visualMeasureOverlay.parentElement.removeChild(visualMeasureOverlay)
  visualMeasureOverlay = null
  visualMeasureLineX = null
  visualMeasureLineY = null
  visualMeasureLabelX = null
  visualMeasureLabelY = null
  hideMeasureOverlay()
  if (visualRedlineOverlay?.parentElement) visualRedlineOverlay.parentElement.removeChild(visualRedlineOverlay)
  visualRedlineOverlay = null
  visualRedlineLineX = null
  visualRedlineLineY = null
  visualRedlineLabelX = null
  visualRedlineLabelY = null
  hideRedlineOverlay()
  if (visualMarqueeOverlay?.parentElement) visualMarqueeOverlay.parentElement.removeChild(visualMarqueeOverlay)
  visualMarqueeOverlay = null
  visualMarqueeMoveHandler = null
  visualMarqueeUpHandler = null
  marqueeState = null
  if (visualGridOverlay?.parentElement) visualGridOverlay.parentElement.removeChild(visualGridOverlay)
  if (visualLayoutColumnsOverlay?.parentElement) visualLayoutColumnsOverlay.parentElement.removeChild(visualLayoutColumnsOverlay)
  if (visualRulersOverlay?.parentElement) visualRulersOverlay.parentElement.removeChild(visualRulersOverlay)
  if (visualLayoutGuideLayer?.parentElement) visualLayoutGuideLayer.parentElement.removeChild(visualLayoutGuideLayer)
  visualGridOverlay = null
  visualLayoutColumnsOverlay = null
  visualRulersOverlay = null
  visualLayoutGuideLayer = null
  visualGuideDragMoveHandler = null
  visualGuideDragUpHandler = null
  hideFlowInsertionLine()
  if (visualFlowInsertionLine?.parentElement) visualFlowInsertionLine.parentElement.removeChild(visualFlowInsertionLine)
  visualFlowInsertionLine = null
  if (visualTextToolbar?.parentElement) visualTextToolbar.parentElement.removeChild(visualTextToolbar)
  visualTextToolbar = null
  inlineTextEditState = null
  suppressFrameClickOnce = false
  canvasSpacePressed = false
  if (canvasZoomHudTimer !== null) {
    window.clearTimeout(canvasZoomHudTimer)
    canvasZoomHudTimer = null
  }
  visualFrameDocument = null
  visualLayerScanToken += 1
  layerScanInProgress.value = false
  clearPreviewTimeout()
  clearPayloadAbortController()
  if (pendingSelectionFrameHandle !== null) {
    window.cancelAnimationFrame(pendingSelectionFrameHandle)
    pendingSelectionFrameHandle = null
  }
  if (_clickThrottleTimer !== null) {
    window.clearTimeout(_clickThrottleTimer)
    _clickThrottleTimer = null
  }
  if (dirtyDebounceTimer !== null) { window.clearTimeout(dirtyDebounceTimer); dirtyDebounceTimer = null }
  clearAutoSaveTimer()
  clearComputedStyleTask()
})
</script>
