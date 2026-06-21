<template>
  <aside class="fig-panel fig-panel-right" dir="ltr" :class="[`fig-inspector-density-${resolvedInspectorDensity}`]">
    <div class="fig-inspector-header">
      <template v-if="visualSelectedLayer">
        <div class="fig-inspector-node">
          <span class="fig-node-tag">{{ visualSelectedLayer.tag }}</span>
          <span class="fig-node-label">{{ visualSelectedLayer.label }}</span>
        </div>
        <code class="fig-node-selector">{{ visualSelectedLayer.selector || '—' }}</code>
      </template>
      <div v-else class="fig-inspector-empty">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>
        <span>روی یک المنت کلیک کن</span>
      </div>
    </div>

    <template v-if="!visualSelectedLayer">
      <InspectorSection
        title="Variables"
        icon="variables"
        :open="isStyleSectionExpanded('__variables__')"
        @toggle="$emit('toggle-style-section', '__variables__')"
      >
        <input
          class="fig-prop-input"
          type="text"
          dir="ltr"
          :value="cssVariableQuery"
          placeholder="search variable..."
          @input="$emit('update:css-variable-query', $event.target.value)"
        />
        <div v-if="!cssVariables.length" class="fig-inspector-no-style">متغیر CSS پیدا نشد.</div>
        <label v-for="row in cssVariables" :key="row.name" class="fig-prop-row">
          <span class="fig-prop-label" dir="ltr">{{ row.name }}</span>
          <div class="fig-prop-control">
            <input
              class="fig-prop-input"
              dir="ltr"
              :value="row.value"
              @input="$emit('update-css-variable', row.name, $event.target.value)"
            />
          </div>
        </label>
      </InspectorSection>

      <InspectorSection
        title="Styles"
        icon="styles"
        :open="isStyleSectionExpanded('__styles__')"
        @toggle="$emit('toggle-style-section', '__styles__')"
      >
        <div class="fig-inspector-style-group">
          <strong>Text styles</strong>
          <div v-if="!textStyleTokens.length" class="fig-inspector-no-style">text style ندارد.</div>
          <div v-for="token in textStyleTokens" :key="`text-${token.name}`" class="fig-token-row">
            <span class="fig-token-label" dir="ltr">{{ token.name }}</span>
            <code class="fig-token-value" dir="ltr">{{ token.value }}</code>
          </div>
        </div>
        <div class="fig-inspector-style-group">
          <strong>Color styles</strong>
          <div v-if="!colorStyleTokens.length" class="fig-inspector-no-style">color style ندارد.</div>
          <div v-for="token in colorStyleTokens" :key="`color-${token.name}`" class="fig-token-row">
            <span class="fig-token-dot" :style="{ background: token.value || '#111' }"></span>
            <span class="fig-token-label" dir="ltr">{{ token.name }}</span>
            <code class="fig-token-value" dir="ltr">{{ token.value }}</code>
          </div>
        </div>
      </InspectorSection>

      <InspectorSection
        title="Token Collections"
        icon="variables"
        :open="isStyleSectionExpanded('__tokens__')"
        @toggle="$emit('toggle-style-section', '__tokens__')"
      >
        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Collection</span>
          <div class="fig-component-variant-row">
            <select
              class="fig-prop-select"
              dir="ltr"
              :value="activeTokenCollectionId"
              @change="$emit('set-token-collection', $event.target.value)"
            >
              <option v-for="row in tokenCollectionItems" :key="`token-col-${row.id}`" :value="row.id">{{ row.name }}</option>
            </select>
            <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="$emit('add-token-collection')">New</button>
          </div>
        </label>

        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Mode</span>
          <select
            class="fig-prop-select"
            dir="ltr"
            :value="activeTokenMode"
            @change="$emit('set-token-mode', $event.target.value)"
          >
            <option v-for="mode in tokenModeOptions" :key="`token-mode-${mode}`" :value="mode">{{ mode }}</option>
          </select>
        </label>

        <div class="fig-component-variant-row">
          <input
            class="fig-prop-input"
            dir="ltr"
            :value="tokenDraftName"
            placeholder="token name (--color-primary)"
            @input="$emit('update:token-draft-name', $event.target.value)"
          />
          <input
            class="fig-prop-input"
            dir="ltr"
            :value="tokenDraftValue"
            placeholder="value (#fff / @alias)"
            @input="$emit('update:token-draft-value', $event.target.value)"
          />
          <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="$emit('add-token')">Add</button>
        </div>

        <div v-if="!tokenRows.length" class="fig-inspector-no-style">توکنی تعریف نشده.</div>
        <div v-else class="fig-raw-style-list">
          <div v-for="row in tokenRows" :key="`token-row-${row.name}`" class="fig-raw-style-item">
            <span class="fig-raw-style-key" dir="ltr">{{ row.name }}</span>
            <input
              class="fig-prop-input"
              dir="ltr"
              :value="row.rawValue"
              :placeholder="row.aliasTarget ? `@${row.aliasTarget}` : ''"
              @input="$emit('update-token-value', row.name, $event.target.value)"
            />
            <button class="fig-btn fig-btn-danger fig-btn-xs" type="button" @click="$emit('remove-token', row.name)">x</button>
          </div>
          <div v-for="row in tokenRows" :key="`token-meta-${row.name}`" class="fig-token-row">
            <span class="fig-token-label" dir="ltr">{{ row.name }}</span>
            <code class="fig-token-value" dir="ltr">
              {{ row.hasCycle ? 'Alias cycle' : row.resolvedValue || '—' }}
            </code>
            <span class="fig-token-value">usage: {{ row.usageCount }}</span>
          </div>
        </div>

        <div class="fig-component-variant-row">
          <input
            class="fig-prop-input"
            dir="ltr"
            :value="tokenBulkFrom"
            placeholder="bulk from (--old-token)"
            @input="$emit('update:token-bulk-from', $event.target.value)"
          />
          <input
            class="fig-prop-input"
            dir="ltr"
            :value="tokenBulkTo"
            placeholder="bulk to (--new-token)"
            @input="$emit('update:token-bulk-to', $event.target.value)"
          />
          <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="$emit('apply-token-bulk-replace')">Replace</button>
        </div>
      </InspectorSection>
    </template>

    <template v-if="visualSelectedLayer">
      <div class="fig-inspector-quick-actions">
        <button class="fig-btn fig-btn-ghost fig-btn-sm" type="button" @click="$emit('duplicate-selected')">Duplicate</button>
        <button class="fig-btn fig-btn-ghost fig-btn-sm" type="button" @click="$emit('add-element')">Add</button>
        <button class="fig-btn fig-btn-ghost fig-btn-sm" type="button" :disabled="selectedVisualCount < 2" @click="$emit('group-selection')">Group</button>
        <button class="fig-btn fig-btn-ghost fig-btn-sm" type="button" @click="$emit('ungroup-selection')">Ungroup</button>
      </div>
      <div class="fig-inspector-selection-meta">{{ selectedVisualCount }} item selected</div>
      <div class="fig-inspector-level-switch">
        <button
          type="button"
          class="fig-level-btn"
          :class="{ 'fig-level-btn-active': inspectorLevel === 'basic' }"
          @click="setInspectorLevel('basic')"
        >
          Basic
        </button>
        <button
          type="button"
          class="fig-level-btn"
          :class="{ 'fig-level-btn-active': inspectorLevel === 'advanced' }"
          @click="setInspectorLevel('advanced')"
        >
          Advanced
        </button>
      </div>
      <div class="fig-inspector-global-search">
        <input
          :value="inspectorStyleQuery"
          class="fig-prop-input"
          type="text"
          placeholder="Search section or property... (dimension, width)"
          dir="ltr"
          @input="$emit('update:inspector-style-query', $event.target.value)"
        />
      </div>

      <InspectorSection
        v-if="hasInspectorQuery"
        title="Search Results"
        icon="styles"
        :open="isStyleSectionExpanded('__search_results__')"
        @toggle="$emit('toggle-style-section', '__search_results__')"
      >
        <div v-if="!filteredStyleSections.length" class="fig-inspector-no-style fig-inspector-no-style-inline">
          نتیجه‌ای پیدا نشد.
        </div>
        <div
          v-for="section in filteredStyleSections"
          :key="`search-${section.title}`"
          class="fig-all-properties-section"
        >
          <div class="fig-all-properties-section-title">{{ section.title }}</div>
          <StyleFieldControl
            v-for="field in section.fields"
            :key="`search-field-${section.title}-${field.key}`"
            :field="field"
            :value="visualProps[field.key]"
            :options="getFieldOptions(field.key)"
            :select-value="getFieldSelectValue(field.key)"
            :show-custom-input="shouldShowCustomInput(field.key)"
            :mixed="Boolean(mixedFieldKeys[field.key])"
            :is-color="isColorField(field.key) || field.isColor"
            :overridden="isFieldOverridden(field.key)"
            :highlight-query="inspectorStyleQuery"
            @preset-change="(fieldKey, value) => $emit('field-preset-change', fieldKey, value)"
            @input-change="(fieldKey, value) => $emit('field-input-change', fieldKey, value)"
            @color-change="(fieldKey, value) => $emit('field-color-change', fieldKey, value)"
            @revert-field="(fieldKey) => $emit('field-revert', fieldKey)"
          />
        </div>
      </InspectorSection>

      <InspectorSection
        v-if="isBasicInspector && !hasInspectorQuery"
        title="Content"
        icon="typography"
        :open="isStyleSectionExpanded('__text__')"
        @toggle="$emit('toggle-style-section', '__text__')"
      >
        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Text</span>
          <textarea
            class="fig-prop-textarea"
            rows="2"
            :value="mixedFieldKeys.text_content ? '' : visualProps.text_content"
            :placeholder="mixedFieldKeys.text_content ? 'Mixed values' : ''"
            @input="onMixedAwareInput('text_content', $event.target.value, { allowEmptyForMixed: false })"
          ></textarea>
        </label>
        <div class="fig-inspector-inline-tip">دابل‌کلیک روی متن داخل canvas برای inline editing</div>
      </InspectorSection>

      <InspectorSection
        v-if="isBasicInspector && !hasInspectorQuery"
        title="Image"
        icon="fill"
        :open="isStyleSectionExpanded('__image_basic__')"
        @toggle="$emit('toggle-style-section', '__image_basic__')"
      >
        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Target</span>
          <div class="fig-image-target-meta">
            <strong>{{ imageTargetTypeLabel }}</strong>
            <small v-if="visualSelectedLayer?.tag" dir="ltr">{{ visualSelectedLayer.tag }}</small>
          </div>
        </label>
        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Source</span>
          <div class="fig-component-variant-row">
            <input
              class="fig-prop-input"
              dir="ltr"
              :value="imageSourceDraft"
              placeholder="/files/example.jpg or https://..."
              @input="onImageSourceDraftInput($event.target.value)"
            />
            <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" :disabled="!canApplyImageSource" @click="emitImageSourceApply">
              Apply
            </button>
          </div>
        </label>
        <div class="fig-image-upload-row">
          <button
            class="fig-btn fig-btn-ghost fig-btn-xs"
            type="button"
            :disabled="imageUploading"
            @click="triggerInspectorImageUpload"
          >
            {{ imageUploading ? 'Uploading...' : 'Upload image' }}
          </button>
          <button
            class="fig-btn fig-btn-ghost fig-btn-xs"
            type="button"
            :disabled="imageLibraryLoading"
            @click="$emit('refresh-image-assets')"
          >
            {{ imageLibraryLoading ? 'Loading...' : 'Refresh library' }}
          </button>
          <input
            ref="inspectorImageUploadInput"
            type="file"
            accept="image/*"
            class="fig-upload-hidden-input"
            @change="onInspectorImageFileChange"
          />
        </div>
        <input
          class="fig-prop-input"
          type="text"
          dir="ltr"
          :value="imageAssetQuery"
          placeholder="search system images..."
          @input="$emit('update:image-asset-query', $event.target.value)"
        />
        <div v-if="!imageAssetItems.length" class="fig-inspector-no-style">تصویری در سیستم پیدا نشد.</div>
        <div v-else class="fig-image-library-list">
          <button
            v-for="item in imageAssetItems.slice(0, 8)"
            :key="`img-asset-${item.id || item.url}`"
            type="button"
            class="fig-image-library-item"
            @click="$emit('apply-image-asset', item)"
          >
            <span class="fig-image-library-thumb-wrap">
              <img :src="item.previewUrl || item.url" :alt="item.name || 'image'" class="fig-image-library-thumb" loading="lazy" />
            </span>
            <span class="fig-image-library-meta">
              <strong>{{ item.name || 'Image' }}</strong>
              <small dir="ltr">{{ item.url }}</small>
            </span>
          </button>
        </div>
      </InspectorSection>

      <InspectorSection
        v-if="isBasicInspector && !hasInspectorQuery"
        title="Position"
        icon="position"
        :open="isStyleSectionExpanded('__position_basic__')"
        @toggle="$emit('toggle-style-section', '__position_basic__')"
      >
        <div class="fig-position-mode">
          <button
            v-for="item in quickPositionModeItems"
            :key="`pos-mode-${item.value}`"
            type="button"
            class="fig-position-mode-btn"
            :class="{ 'fig-position-mode-btn-active': visualProps.position === item.value && !mixedFieldKeys.position }"
            :title="item.label"
            @click="onMixedAwareSet('position', item.value)"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path v-for="(line, idx) in item.iconPaths" :key="`p-${item.value}-${idx}`" :d="line"></path>
            </svg>
          </button>
        </div>
        <div class="fig-position-grid">
          <StyleFieldControl
            v-for="field in quickPositionFields"
            :key="`quick-pos-${field.key}`"
            :field="field"
            :value="visualProps[field.key]"
            :options="getFieldOptions(field.key)"
            :select-value="getFieldSelectValue(field.key)"
            :show-custom-input="shouldShowCustomInput(field.key)"
            :mixed="Boolean(mixedFieldKeys[field.key])"
            :is-color="false"
            :overridden="isFieldOverridden(field.key)"
            @preset-change="(fieldKey, value) => $emit('field-preset-change', fieldKey, value)"
            @input-change="(fieldKey, value) => $emit('field-input-change', fieldKey, value)"
            @revert-field="(fieldKey) => $emit('field-revert', fieldKey)"
          />
        </div>
      </InspectorSection>

      <InspectorSection
        v-if="isBasicInspector && !hasInspectorQuery"
        title="Auto Layout"
        icon="layout"
        :open="isStyleSectionExpanded('__autolayout__')"
        @toggle="$emit('toggle-style-section', '__autolayout__')"
      >
        <div class="fig-constraint-group">
          <span class="fig-constraint-label">Mode</span>
          <div class="fig-constraint-buttons">
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.display === 'flex' }" @click="$emit('apply-visual-field', 'display', 'flex')">Flex</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.display === 'grid' }" @click="$emit('apply-visual-field', 'display', 'grid')">Grid</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.display === 'block' }" @click="$emit('apply-visual-field', 'display', 'block')">Block</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.display === 'none' }" @click="$emit('apply-visual-field', 'display', 'none')">None</button>
          </div>
        </div>
        <div class="fig-constraint-group">
          <span class="fig-constraint-label">Direction</span>
          <div class="fig-constraint-buttons">
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.flexDirection === 'row' }" @click="$emit('apply-visual-field', 'flexDirection', 'row')">Row</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.flexDirection === 'column' }" @click="$emit('apply-visual-field', 'flexDirection', 'column')">Column</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.flexWrap === 'nowrap' }" @click="$emit('apply-visual-field', 'flexWrap', 'nowrap')">No Wrap</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.flexWrap === 'wrap' }" @click="$emit('apply-visual-field', 'flexWrap', 'wrap')">Wrap</button>
          </div>
        </div>
        <div class="fig-constraint-group">
          <span class="fig-constraint-label">Child Position</span>
          <div class="fig-constraint-buttons">
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.position === 'relative' || visualProps.position === 'static' }" @click="onMixedAwareSet('position', 'relative')">Auto</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.position === 'absolute' }" @click="onMixedAwareSet('position', 'absolute')">Absolute</button>
          </div>
        </div>
        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Justify</span>
          <select class="fig-prop-select" dir="ltr" :value="visualProps.justifyContent" @change="$emit('apply-visual-field', 'justifyContent', $event.target.value)">
            <option value="">—</option>
            <option value="flex-start">flex-start</option>
            <option value="center">center</option>
            <option value="flex-end">flex-end</option>
            <option value="space-between">space-between</option>
            <option value="space-around">space-around</option>
            <option value="space-evenly">space-evenly</option>
          </select>
        </label>
        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Align</span>
          <select class="fig-prop-select" dir="ltr" :value="visualProps.alignItems" @change="$emit('apply-visual-field', 'alignItems', $event.target.value)">
            <option value="">—</option>
            <option value="stretch">stretch</option>
            <option value="flex-start">flex-start</option>
            <option value="center">center</option>
            <option value="flex-end">flex-end</option>
            <option value="baseline">baseline</option>
          </select>
        </label>
        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Gap</span>
          <input class="fig-prop-input" dir="ltr" :value="visualProps.gap" placeholder="8px" @input="$emit('apply-visual-field', 'gap', $event.target.value)" />
        </label>
        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Padding</span>
          <input class="fig-prop-input" dir="ltr" :value="visualProps.padding" placeholder="16px" @input="$emit('apply-visual-field', 'padding', $event.target.value)" />
        </label>
      </InspectorSection>

      <template v-if="isBasicInspector && !hasInspectorQuery">
        <InspectorSection
          v-for="section in basicVisualSections"
          :key="`basic-${section.title}`"
          :title="section.title"
          :icon="section.icon"
          :open="isStyleSectionExpanded(section.key)"
          @toggle="$emit('toggle-style-section', section.key)"
        >
          <StyleFieldControl
            v-for="field in section.fields"
            :key="`basic-${section.title}-${field.key}`"
            :field="field"
            :value="visualProps[field.key]"
            :options="getFieldOptions(field.key)"
            :select-value="getFieldSelectValue(field.key)"
            :show-custom-input="shouldShowCustomInput(field.key)"
            :mixed="Boolean(mixedFieldKeys[field.key])"
            :is-color="isColorField(field.key) || field.isColor"
            :overridden="isFieldOverridden(field.key)"
            @preset-change="(fieldKey, value) => $emit('field-preset-change', fieldKey, value)"
            @input-change="(fieldKey, value) => $emit('field-input-change', fieldKey, value)"
            @color-change="(fieldKey, value) => $emit('field-color-change', fieldKey, value)"
            @revert-field="(fieldKey) => $emit('field-revert', fieldKey)"
          />
        </InspectorSection>
      </template>

      <InspectorSection
        v-if="isBasicInspector && !hasInspectorQuery"
        title="Typography"
        icon="typography"
        :open="isStyleSectionExpanded('__typography_basic__')"
        @toggle="$emit('toggle-style-section', '__typography_basic__')"
      >
        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Font Family</span>
          <select class="fig-prop-select" dir="ltr" :value="mixedFieldKeys.fontFamily ? '__mixed__' : visualProps.fontFamily" @change="onMixedAwareSelect('fontFamily', $event.target.value)">
            <option value="__mixed__" disabled>Mixed</option>
            <option value="">—</option>
            <option v-for="opt in getFieldOptions('fontFamily')" :key="`font-family-${opt}`" :value="opt">{{ opt }}</option>
          </select>
        </label>
        <div class="fig-inspector-typo-grid">
          <label class="fig-prop-row fig-prop-row-full">
            <span class="fig-prop-label">Size</span>
            <input class="fig-prop-input" dir="ltr" :value="mixedFieldKeys.fontSize ? '' : visualProps.fontSize" :placeholder="mixedFieldKeys.fontSize ? 'Mixed' : '16px'" @input="onMixedAwareInput('fontSize', $event.target.value)" />
          </label>
          <label class="fig-prop-row fig-prop-row-full">
            <span class="fig-prop-label">Weight</span>
            <select class="fig-prop-select" dir="ltr" :value="mixedFieldKeys.fontWeight ? '__mixed__' : visualProps.fontWeight" @change="onMixedAwareSelect('fontWeight', $event.target.value)">
              <option value="__mixed__" disabled>Mixed</option>
              <option value="">—</option>
              <option v-for="opt in getFieldOptions('fontWeight')" :key="`font-weight-${opt}`" :value="opt">{{ opt }}</option>
            </select>
          </label>
          <label class="fig-prop-row fig-prop-row-full">
            <span class="fig-prop-label">Line Height</span>
            <input class="fig-prop-input" dir="ltr" :value="mixedFieldKeys.lineHeight ? '' : visualProps.lineHeight" :placeholder="mixedFieldKeys.lineHeight ? 'Mixed' : '1.7'" @input="onMixedAwareInput('lineHeight', $event.target.value)" />
          </label>
          <label class="fig-prop-row fig-prop-row-full">
            <span class="fig-prop-label">Letter Spacing</span>
            <input class="fig-prop-input" dir="ltr" :value="mixedFieldKeys.letterSpacing ? '' : visualProps.letterSpacing" :placeholder="mixedFieldKeys.letterSpacing ? 'Mixed' : '0'" @input="onMixedAwareInput('letterSpacing', $event.target.value)" />
          </label>
        </div>
        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Paragraph Spacing</span>
          <input
            class="fig-prop-input"
            dir="ltr"
            :value="mixedFieldKeys.paragraphSpacing ? '' : visualProps.paragraphSpacing"
            :placeholder="mixedFieldKeys.paragraphSpacing ? 'Mixed' : '8px'"
            @input="onMixedAwareParagraphSpacing($event.target.value)"
          />
        </label>
        <div class="fig-constraint-group">
          <span class="fig-constraint-label">Align</span>
          <div class="fig-constraint-buttons">
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.textAlign === 'left' && !mixedFieldKeys.textAlign }" @click="onMixedAwareSet('textAlign', 'left')">Left</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.textAlign === 'center' && !mixedFieldKeys.textAlign }" @click="onMixedAwareSet('textAlign', 'center')">Center</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.textAlign === 'right' && !mixedFieldKeys.textAlign }" @click="onMixedAwareSet('textAlign', 'right')">Right</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.textAlign === 'justify' && !mixedFieldKeys.textAlign }" @click="onMixedAwareSet('textAlign', 'justify')">Justify</button>
          </div>
        </div>
        <div class="fig-constraint-group">
          <span class="fig-constraint-label">List</span>
          <div class="fig-constraint-buttons">
            <button type="button" class="fig-constraint-btn" @click="$emit('text-list-command', 'ul')">UL</button>
            <button type="button" class="fig-constraint-btn" @click="$emit('text-list-command', 'ol')">OL</button>
            <button type="button" class="fig-constraint-btn" @click="$emit('text-list-command', 'indent')">Indent</button>
            <button type="button" class="fig-constraint-btn" @click="$emit('text-list-command', 'outdent')">Outdent</button>
          </div>
        </div>
      </InspectorSection>

      <InspectorSection
        v-if="isAdvancedInspector && !hasInspectorQuery"
        title="Shared Text Styles"
        icon="styles"
        :open="isStyleSectionExpanded('__shared_text_style__')"
        @toggle="$emit('toggle-style-section', '__shared_text_style__')"
      >
        <div class="fig-component-variant-row">
          <select class="fig-prop-select" dir="ltr" :value="sharedStyleDraftId" @change="onSharedStyleDraftInput($event.target.value)">
            <option value="">Select style...</option>
            <option v-for="item in sharedTextStyleItems" :key="`shared-style-${item.id}`" :value="item.id">{{ item.name }}</option>
          </select>
          <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" :disabled="!sharedStyleDraftId" @click="applySharedStyle">Apply</button>
          <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" :disabled="!sharedStyleDraftId" @click="updateSharedStyle">Update</button>
          <button class="fig-btn fig-btn-danger fig-btn-xs" type="button" :disabled="!selectedSharedTextStyleId" @click="$emit('detach-shared-text-style')">Detach</button>
        </div>
        <div v-if="selectedSharedTextStyleId" class="fig-shared-style-meta">
          Linked: <code dir="ltr">{{ selectedSharedTextStyleId }}</code>
        </div>
      </InspectorSection>

      <InspectorSection
        v-if="isAdvancedInspector && !hasInspectorQuery"
        title="Text Style Runs"
        icon="typography"
        :open="isStyleSectionExpanded('__text_runs__')"
        @toggle="$emit('toggle-style-section', '__text_runs__')"
      >
        <div class="fig-constraint-buttons">
          <button type="button" class="fig-constraint-btn" @click="$emit('apply-inline-text-command', 'bold')">B</button>
          <button type="button" class="fig-constraint-btn" @click="$emit('apply-inline-text-command', 'italic')">I</button>
          <button type="button" class="fig-constraint-btn" @click="$emit('apply-inline-text-command', 'underline')">U</button>
        </div>
        <div class="fig-component-variant-row">
          <input
            class="fig-prop-input"
            dir="ltr"
            type="number"
            min="8"
            max="180"
            :value="styleRunDraft.fontSize"
            placeholder="size"
            @input="onStyleRunDraftInput('fontSize', $event.target.value)"
          />
          <input
            class="fig-prop-input"
            dir="ltr"
            :value="styleRunDraft.letterSpacing"
            placeholder="letter spacing"
            @input="onStyleRunDraftInput('letterSpacing', $event.target.value)"
          />
          <input
            class="fig-prop-input"
            type="color"
            :value="styleRunDraft.color"
            @input="onStyleRunDraftInput('color', $event.target.value)"
          />
          <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="applyStyleRunDraft">Apply</button>
        </div>
      </InspectorSection>

      <InspectorSection
        v-if="isAdvancedInspector && !hasInspectorQuery"
        title="Advanced Text"
        icon="typography"
        :open="isStyleSectionExpanded('__textengine__')"
        @toggle="$emit('toggle-style-section', '__textengine__')"
      >
        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Paragraph Style</span>
          <div class="fig-component-variant-row">
            <select
              class="fig-prop-select"
              dir="ltr"
              :value="textParagraphPreset"
              @change="$emit('update:text-paragraph-preset', $event.target.value)"
            >
              <option v-for="preset in textParagraphPresetOptions" :key="`p-${preset.key}`" :value="preset.key">{{ preset.label }}</option>
            </select>
            <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="$emit('apply-text-paragraph-preset')">Apply</button>
          </div>
        </label>

        <div class="fig-constraint-buttons">
          <button type="button" class="fig-constraint-btn" @click="$emit('text-list-command', 'ul')">UL</button>
          <button type="button" class="fig-constraint-btn" @click="$emit('text-list-command', 'ol')">OL</button>
          <button type="button" class="fig-constraint-btn" @click="$emit('text-list-command', 'indent')">Indent</button>
          <button type="button" class="fig-constraint-btn" @click="$emit('text-list-command', 'outdent')">Outdent</button>
        </div>

        <div class="fig-component-variant-row">
          <input
            class="fig-prop-input"
            dir="ltr"
            :value="textOpenType"
            placeholder="font-feature-settings"
            @input="$emit('update:text-opentype', $event.target.value)"
          />
          <input
            class="fig-prop-input"
            dir="ltr"
            :value="textLigatures"
            placeholder="font-variant-ligatures"
            @input="$emit('update:text-ligatures', $event.target.value)"
          />
          <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="$emit('apply-text-opentype')">Apply</button>
        </div>

        <div class="fig-component-variant-row">
          <input
            class="fig-prop-input"
            dir="ltr"
            type="number"
            min="2"
            max="64"
            :value="textBaselineStep"
            placeholder="baseline"
            @input="$emit('update:text-baseline-step', $event.target.value)"
          />
          <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="$emit('snap-text-baseline')">Snap Baseline</button>
        </div>

        <div class="fig-component-variant-row">
          <input
            class="fig-prop-input"
            dir="ltr"
            :value="textFindQuery"
            placeholder="find"
            @input="$emit('update:text-find-query', $event.target.value)"
          />
          <input
            class="fig-prop-input"
            dir="ltr"
            :value="textReplaceValue"
            placeholder="replace"
            @input="$emit('update:text-replace-value', $event.target.value)"
          />
          <select
            class="fig-prop-select"
            dir="ltr"
            :value="textReplaceScope"
            @change="$emit('update:text-replace-scope', $event.target.value)"
          >
            <option value="selection">Selection</option>
            <option value="page">Page</option>
          </select>
          <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="$emit('apply-text-find-replace')">Replace</button>
        </div>
      </InspectorSection>

      <InspectorSection
        v-if="isAdvancedInspector && !hasInspectorQuery"
        title="Constraints"
        icon="position"
        :open="isStyleSectionExpanded('__constraints__')"
        @toggle="$emit('toggle-style-section', '__constraints__')"
      >
        <div class="fig-constraint-group">
          <span class="fig-constraint-label">Pin (9-Point)</span>
          <div class="fig-constraint-matrix">
            <button
              v-for="anchor in constraintAnchorItems"
              :key="`anchor-${anchor.id}`"
              type="button"
              class="fig-constraint-matrix-btn"
              :class="{ 'fig-constraint-matrix-btn-active': activeConstraintAnchor === anchor.id }"
              :title="anchor.label"
              @click="$emit('set-constraint-anchor', anchor.id)"
            >
              <span></span>
            </button>
          </div>
        </div>
        <div class="fig-constraint-group">
          <span class="fig-constraint-label">Horizontal</span>
          <div class="fig-constraint-buttons">
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': selectedConstraintState.horizontal === 'left' }" @click="$emit('set-constraint', 'horizontal', 'left')">Left</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': selectedConstraintState.horizontal === 'center' }" @click="$emit('set-constraint', 'horizontal', 'center')">Center</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': selectedConstraintState.horizontal === 'right' }" @click="$emit('set-constraint', 'horizontal', 'right')">Right</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': selectedConstraintState.horizontal === 'stretch' }" @click="$emit('set-constraint', 'horizontal', 'stretch')">Stretch</button>
          </div>
        </div>
        <div class="fig-constraint-group">
          <span class="fig-constraint-label">Vertical</span>
          <div class="fig-constraint-buttons">
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': selectedConstraintState.vertical === 'top' }" @click="$emit('set-constraint', 'vertical', 'top')">Top</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': selectedConstraintState.vertical === 'center' }" @click="$emit('set-constraint', 'vertical', 'center')">Center</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': selectedConstraintState.vertical === 'bottom' }" @click="$emit('set-constraint', 'vertical', 'bottom')">Bottom</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': selectedConstraintState.vertical === 'stretch' }" @click="$emit('set-constraint', 'vertical', 'stretch')">Stretch</button>
          </div>
        </div>
        <div class="fig-constraint-group">
          <span class="fig-constraint-label">Size (Both)</span>
          <div class="fig-constraint-buttons">
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': selectedConstraintState.size === 'fixed' }" @click="$emit('set-constraint', 'size', 'fixed')">Fixed</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': selectedConstraintState.size === 'hug' }" @click="$emit('set-constraint', 'size', 'hug')">Hug</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': selectedConstraintState.size === 'fill' }" @click="$emit('set-constraint', 'size', 'fill')">Fill</button>
          </div>
        </div>
        <div class="fig-constraint-group">
          <span class="fig-constraint-label">Width Mode</span>
          <div class="fig-constraint-buttons fig-constraint-buttons-3">
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': (selectedConstraintState.sizeWidth || selectedConstraintState.size) === 'fixed' }" @click="$emit('set-constraint', 'size-width', 'fixed')">Fixed</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': (selectedConstraintState.sizeWidth || selectedConstraintState.size) === 'hug' }" @click="$emit('set-constraint', 'size-width', 'hug')">Hug</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': (selectedConstraintState.sizeWidth || selectedConstraintState.size) === 'fill' }" @click="$emit('set-constraint', 'size-width', 'fill')">Fill</button>
          </div>
        </div>
        <div class="fig-constraint-group">
          <span class="fig-constraint-label">Height Mode</span>
          <div class="fig-constraint-buttons fig-constraint-buttons-3">
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': (selectedConstraintState.sizeHeight || selectedConstraintState.size) === 'fixed' }" @click="$emit('set-constraint', 'size-height', 'fixed')">Fixed</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': (selectedConstraintState.sizeHeight || selectedConstraintState.size) === 'hug' }" @click="$emit('set-constraint', 'size-height', 'hug')">Hug</button>
            <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': (selectedConstraintState.sizeHeight || selectedConstraintState.size) === 'fill' }" @click="$emit('set-constraint', 'size-height', 'fill')">Fill</button>
          </div>
        </div>
      </InspectorSection>

      <InspectorSection
        v-if="isAdvancedInspector && !hasInspectorQuery"
        title="Prototype"
        icon="layout"
        :open="isStyleSectionExpanded('__prototype__')"
        @toggle="$emit('toggle-style-section', '__prototype__')"
      >
        <div class="fig-constraint-group">
          <span class="fig-constraint-label">Preview Flow</span>
          <div class="fig-constraint-buttons">
            <button
              type="button"
              class="fig-constraint-btn"
              :class="{ 'fig-constraint-btn-active': prototypeModelEnabled }"
              @click="$emit('toggle-prototype-preview')"
            >
              {{ prototypeModelEnabled ? 'ON' : 'OFF' }}
            </button>
          </div>
        </div>

        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Frame ID</span>
          <div class="fig-component-variant-row">
            <input
              class="fig-prop-input"
              dir="ltr"
              :value="prototypeFrameIdDraft"
              placeholder="home-main"
              @input="$emit('update:prototype-frame-id-draft', $event.target.value)"
            />
            <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="$emit('set-prototype-frame')">Set</button>
            <button class="fig-btn fig-btn-danger fig-btn-xs" type="button" @click="$emit('remove-prototype-frame')">Clear</button>
          </div>
        </label>

        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Start Frame</span>
          <select
            class="fig-prop-select"
            dir="ltr"
            :value="prototypeStartFrameId"
            @change="$emit('set-prototype-start-frame', $event.target.value)"
          >
            <option value="">auto</option>
            <option v-for="row in prototypeFrameOptions" :key="`start-${row.id}`" :value="row.id">{{ row.label }}</option>
          </select>
        </label>

        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Target Frame</span>
          <select
            class="fig-prop-select"
            dir="ltr"
            :value="prototypeLinkTargetFrameId"
            @change="$emit('update:prototype-link-target-frame-id', $event.target.value)"
          >
            <option value="">Select frame...</option>
            <option v-for="row in prototypeFrameOptions" :key="`target-${row.id}`" :value="row.id">{{ row.label }}</option>
          </select>
        </label>

        <div class="fig-component-variant-row">
          <select
            class="fig-prop-select"
            dir="ltr"
            :value="prototypeLinkTransition"
            @change="$emit('update:prototype-link-transition', $event.target.value)"
          >
            <option value="instant">instant</option>
            <option value="dissolve">dissolve</option>
            <option value="smart-animate">smart-animate</option>
          </select>
          <input
            class="fig-prop-input"
            dir="ltr"
            type="number"
            min="60"
            max="8000"
            :value="prototypeLinkDurationMs"
            @input="$emit('update:prototype-link-duration-ms', $event.target.value)"
          />
          <button
            type="button"
            class="fig-constraint-btn"
            :class="{ 'fig-constraint-btn-active': prototypeLinkSmartAnimate }"
            @click="$emit('toggle:prototype-link-smart-animate')"
          >
            Smart
          </button>
        </div>

        <div class="fig-component-actions">
          <button class="fig-btn fig-btn-ghost fig-btn-sm" type="button" @click="$emit('set-prototype-link')">Set Link</button>
          <button class="fig-btn fig-btn-danger fig-btn-sm" type="button" @click="$emit('remove-prototype-link')">Remove Link</button>
        </div>
      </InspectorSection>

      <InspectorSection
        v-if="isAdvancedInspector && !hasInspectorQuery"
        title="Component"
        icon="styles"
        :open="isStyleSectionExpanded('__component__')"
        @toggle="$emit('toggle-style-section', '__component__')"
      >
        <div class="fig-component-actions">
          <button class="fig-btn fig-btn-ghost fig-btn-sm" type="button" @click="$emit('create-component-master')">Create Master</button>
          <button class="fig-btn fig-btn-ghost fig-btn-sm" type="button" :disabled="!selectedComponentId" @click="$emit('update-component-master')">Update Master</button>
          <button class="fig-btn fig-btn-ghost fig-btn-sm" type="button" :disabled="!selectedComponentId" @click="$emit('detach-component-instance')">Detach</button>
          <button class="fig-btn fig-btn-ghost fig-btn-sm" type="button" :disabled="!selectedComponentId" @click="$emit('reset-component-overrides')">Reset</button>
          <button class="fig-btn fig-btn-ghost fig-btn-sm" type="button" @click="$emit('publish-component-library')">Publish Library</button>
        </div>
        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Library</span>
          <select
            class="fig-prop-select"
            dir="ltr"
            :value="selectedComponentId"
            @change="$emit('create-component-instance', $event.target.value)"
          >
            <option value="">Select component...</option>
            <option v-for="item in componentLibraryItems" :key="item.id" :value="item.id">{{ item.name }}</option>
          </select>
        </label>
        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Variant</span>
          <div class="fig-component-variant-row">
            <select
              class="fig-prop-select"
              dir="ltr"
              :value="selectedComponentVariant"
              :disabled="!selectedComponentId"
              @change="$emit('apply-component-variant', $event.target.value)"
            >
              <option value="">Select variant...</option>
              <option v-for="variant in selectedComponentVariants" :key="`variant-${variant}`" :value="variant">{{ variant }}</option>
            </select>
            <input
              class="fig-prop-input"
              dir="ltr"
              :value="componentVariantDraft"
              placeholder="new variant"
              @input="$emit('update:component-variant-draft', $event.target.value)"
            />
            <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" :disabled="!selectedComponentId" @click="$emit('create-component-variant')">Save</button>
          </div>
        </label>
        <label class="fig-prop-row fig-prop-row-full">
          <span class="fig-prop-label">Swap Instance</span>
          <div class="fig-component-variant-row">
            <select
              class="fig-prop-select"
              dir="ltr"
              :value="componentSwapTarget"
              @change="$emit('update:component-swap-target', $event.target.value)"
            >
              <option value="">Select target...</option>
              <option v-for="item in componentLibraryItems" :key="`swap-${item.id}`" :value="item.id">{{ item.name }}</option>
            </select>
            <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" :disabled="!selectedComponentId || !componentSwapTarget" @click="$emit('swap-component-instance')">Swap</button>
          </div>
        </label>
        <div v-if="selectedNestedComponentInstances.length" class="fig-component-nested">
          <span class="fig-prop-label">Nested instances</span>
          <button
            v-for="nested in selectedNestedComponentInstances"
            :key="`nested-${nested.nodeId}`"
            type="button"
            class="fig-component-nested-item"
            @click="$emit('select-nested-instance', nested.nodeId)"
          >
            <span dir="ltr">{{ nested.componentId }}</span>
            <small dir="ltr">{{ nested.variant }}</small>
          </button>
        </div>
        <div v-if="variantPropertyRows.length" class="fig-component-variant-props">
          <label v-for="row in variantPropertyRows" :key="`variant-prop-${row.key}`" class="fig-prop-row fig-prop-row-full">
            <span class="fig-prop-label">{{ row.key }}</span>
            <select
              class="fig-prop-select"
              dir="ltr"
              :value="row.value"
              :disabled="!selectedComponentId"
              @change="$emit('set-variant-property', row.key, $event.target.value)"
            >
              <option value="">—</option>
              <option v-for="opt in row.options" :key="`variant-opt-${row.key}-${opt}`" :value="opt">{{ opt }}</option>
            </select>
          </label>
        </div>
      </InspectorSection>

      <InspectorSection
        v-if="isAdvancedInspector && !hasInspectorQuery"
        title="Raw Style"
        icon="styles"
        :open="isStyleSectionExpanded('__rawcss__')"
        @toggle="$emit('toggle-style-section', '__rawcss__')"
      >
        <div class="fig-raw-style-builder">
          <input
            class="fig-prop-input"
            type="text"
            dir="ltr"
            :value="rawStylePropertyQuery"
            placeholder="search property..."
            @input="$emit('update:raw-style-property-query', $event.target.value)"
          />
          <div class="fig-raw-style-row">
            <select
              class="fig-prop-select"
              dir="ltr"
              :value="rawStyleDraft.property"
              @change="$emit('update:raw-style-draft', { property: $event.target.value })"
            >
              <option v-for="prop in rawStylePropertyOptions" :key="`prop-${prop}`" :value="prop">{{ prop }}</option>
              <option value="__custom__">custom...</option>
            </select>
          </div>
          <div class="fig-raw-style-row" v-if="rawStyleDraft.property === '__custom__'">
            <input
              class="fig-prop-input"
              dir="ltr"
              :value="rawStyleDraft.customProperty"
              placeholder="property-name"
              @input="$emit('update:raw-style-draft', { customProperty: $event.target.value })"
            />
          </div>
          <div class="fig-raw-style-row fig-raw-style-row-value">
            <input
              class="fig-prop-input"
              dir="ltr"
              :value="rawStyleDraft.value"
              placeholder="value"
              @input="$emit('update:raw-style-draft', { value: $event.target.value })"
            />
            <button class="fig-btn fig-btn-ghost fig-btn-xs" type="button" @click="$emit('add-raw-style')">Add</button>
          </div>
          <div v-if="!selectedLayerStyleEntries.length" class="fig-inspector-no-style">style سفارشی ندارد.</div>
          <div v-else class="fig-raw-style-list">
            <div v-for="entry in selectedLayerStyleEntries" :key="entry.key" class="fig-raw-style-item">
              <span class="fig-raw-style-key">{{ entry.label }}</span>
              <span class="fig-raw-style-value">{{ entry.value }}</span>
              <button
                class="fig-btn fig-btn-danger fig-btn-xs"
                type="button"
                @click="$emit('remove-raw-style', entry.key)"
              >
                x
              </button>
            </div>
          </div>
        </div>
      </InspectorSection>

      <InspectorSection
        v-if="isAdvancedInspector && !hasInspectorQuery"
        title="Raw HTML"
        icon="typography"
        :open="isStyleSectionExpanded('__rawhtml__')"
        @toggle="$emit('toggle-style-section', '__rawhtml__')"
      >
        <label class="fig-prop-row fig-prop-row-full">
          <textarea
            class="fig-prop-textarea fig-prop-textarea-code"
            rows="7"
            dir="ltr"
            :value="rawHtmlInput"
            placeholder="<div>...</div>"
            @input="$emit('update:raw-html-input', $event.target.value)"
          ></textarea>
        </label>
        <button class="fig-btn fig-btn-ghost fig-btn-sm" type="button" @click="$emit('apply-raw-html')">اعمال Raw HTML</button>
      </InspectorSection>

      <div v-if="isAdvancedInspector && !hasInspectorQuery && !filteredStyleSections.length" class="fig-inspector-no-style">ویژگی‌ای با این جستجو پیدا نشد.</div>

      <InspectorSection
        v-if="isAdvancedInspector && !hasInspectorQuery"
        title="All Properties"
        icon="styles"
        :open="isStyleSectionExpanded('__all_properties__')"
        @toggle="$emit('toggle-style-section', '__all_properties__')"
      >
        <div
          v-for="section in filteredStyleSections"
          :key="`all-${section.title}`"
          class="fig-all-properties-section"
        >
          <div class="fig-all-properties-section-title">{{ section.title }}</div>
          <div class="fig-section-field-search">
            <input
              class="fig-prop-input"
              type="text"
              dir="ltr"
              :value="getSectionFieldQuery(section.title)"
              placeholder="search in section..."
              @input="onSectionFieldQueryInput(section.title, $event.target.value)"
            />
          </div>
          <div v-if="supportsSectionPopover(section.title)" class="fig-section-popover-row">
          <button
            type="button"
            class="fig-btn fig-btn-ghost fig-btn-xs"
            @click="toggleSectionPopover(section.title)"
          >
            {{ isSectionPopoverOpen(section.title) ? 'Hide quick editor' : 'Quick editor' }}
          </button>
          <div v-if="isSectionPopoverOpen(section.title)" class="fig-section-popover">
            <template v-if="section.title === 'Fill'">
              <ColorPickerField
                :model-value="getMixedAwareValue('backgroundColor')"
                :presets="getFieldOptions('backgroundColor')"
                @update:model-value="onMixedAwareSet('backgroundColor', $event)"
              />
              <input
                class="fig-prop-input"
                dir="ltr"
                :value="getMixedAwareValue('opacity')"
                :placeholder="mixedFieldKeys.opacity ? 'Mixed opacity' : '1'"
                @input="onMixedAwareInput('opacity', $event.target.value)"
              />
            </template>
            <template v-else-if="section.title === 'Stroke'">
              <ColorPickerField
                :model-value="getMixedAwareValue('borderColor')"
                :presets="getFieldOptions('borderColor')"
                @update:model-value="onMixedAwareSet('borderColor', $event)"
              />
              <div class="fig-section-popover-grid">
                <input
                  class="fig-prop-input"
                  dir="ltr"
                  :value="getMixedAwareValue('borderWidth')"
                  :placeholder="mixedFieldKeys.borderWidth ? 'Mixed width' : '1px'"
                  @input="onMixedAwareInput('borderWidth', $event.target.value)"
                />
                <input
                  class="fig-prop-input"
                  dir="ltr"
                  :value="getMixedAwareValue('borderRadius')"
                  :placeholder="mixedFieldKeys.borderRadius ? 'Mixed radius' : '8px'"
                  @input="onMixedAwareInput('borderRadius', $event.target.value)"
                />
              </div>
            </template>
            <template v-else-if="section.title === 'Effects'">
              <input
                class="fig-prop-input"
                dir="ltr"
                :value="getMixedAwareValue('boxShadow')"
                :placeholder="mixedFieldKeys.boxShadow ? 'Mixed shadow' : '0 8px 24px rgba(0,0,0,.12)'"
                @input="onMixedAwareInput('boxShadow', $event.target.value)"
              />
              <input
                class="fig-prop-input"
                dir="ltr"
                :value="getMixedAwareValue('transitionDuration')"
                :placeholder="mixedFieldKeys.transitionDuration ? 'Mixed duration' : '0.2s'"
                @input="onMixedAwareInput('transitionDuration', $event.target.value)"
              />
            </template>
            <template v-else-if="section.title === 'Typography'">
              <select
                class="fig-prop-select"
                dir="ltr"
                :value="getMixedAwareSelectValue('fontFamily')"
                @change="onMixedAwareSelect('fontFamily', $event.target.value)"
              >
                <option value="__mixed__" disabled>Mixed</option>
                <option value="">—</option>
                <option v-for="opt in getFieldOptions('fontFamily')" :key="`pop-font-${opt}`" :value="opt">{{ opt }}</option>
              </select>
              <div class="fig-section-popover-grid">
                <input
                  class="fig-prop-input"
                  dir="ltr"
                  :value="getMixedAwareValue('fontSize')"
                  :placeholder="mixedFieldKeys.fontSize ? 'Mixed size' : '16px'"
                  @input="onMixedAwareInput('fontSize', $event.target.value)"
                />
                <select
                  class="fig-prop-select"
                  dir="ltr"
                  :value="getMixedAwareSelectValue('fontWeight')"
                  @change="onMixedAwareSelect('fontWeight', $event.target.value)"
                >
                  <option value="__mixed__" disabled>Mixed</option>
                  <option value="">—</option>
                  <option v-for="opt in getFieldOptions('fontWeight')" :key="`pop-weight-${opt}`" :value="opt">{{ opt }}</option>
                </select>
                <input
                  class="fig-prop-input"
                  dir="ltr"
                  :value="getMixedAwareValue('lineHeight')"
                  :placeholder="mixedFieldKeys.lineHeight ? 'Mixed line-height' : '1.7'"
                  @input="onMixedAwareInput('lineHeight', $event.target.value)"
                />
                <input
                  class="fig-prop-input"
                  dir="ltr"
                  :value="getMixedAwareValue('letterSpacing')"
                  :placeholder="mixedFieldKeys.letterSpacing ? 'Mixed spacing' : '0'"
                  @input="onMixedAwareInput('letterSpacing', $event.target.value)"
                />
              </div>
              <div class="fig-constraint-buttons">
                <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.textAlign === 'left' && !mixedFieldKeys.textAlign }" @click="onMixedAwareSet('textAlign', 'left')">Left</button>
                <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.textAlign === 'center' && !mixedFieldKeys.textAlign }" @click="onMixedAwareSet('textAlign', 'center')">Center</button>
                <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.textAlign === 'right' && !mixedFieldKeys.textAlign }" @click="onMixedAwareSet('textAlign', 'right')">Right</button>
                <button type="button" class="fig-constraint-btn" :class="{ 'fig-constraint-btn-active': visualProps.textAlign === 'justify' && !mixedFieldKeys.textAlign }" @click="onMixedAwareSet('textAlign', 'justify')">Justify</button>
              </div>
            </template>
          </div>
          </div>
          <div v-if="!getSectionFields(section).length" class="fig-inspector-no-style fig-inspector-no-style-inline">
            فیلدی با این جستجو داخل این سکشن پیدا نشد.
          </div>
          <StyleFieldControl
            v-for="field in getSectionFields(section)"
            :key="`all-field-${section.title}-${field.key}`"
            :field="field"
            :value="visualProps[field.key]"
            :options="getFieldOptions(field.key)"
            :select-value="getFieldSelectValue(field.key)"
            :show-custom-input="shouldShowCustomInput(field.key)"
            :mixed="Boolean(mixedFieldKeys[field.key])"
            :is-color="isColorField(field.key) || field.isColor"
            :overridden="isFieldOverridden(field.key)"
            :highlight-query="getSectionFieldQuery(section.title)"
            @preset-change="(fieldKey, value) => $emit('field-preset-change', fieldKey, value)"
            @input-change="(fieldKey, value) => $emit('field-input-change', fieldKey, value)"
            @color-change="(fieldKey, value) => $emit('field-color-change', fieldKey, value)"
            @revert-field="(fieldKey) => $emit('field-revert', fieldKey)"
          />
        </div>
      </InspectorSection>

      <div class="fig-inspector-actions">
        <button class="fig-btn fig-btn-primary fig-btn-sm" :disabled="savingVisual" @click="$emit('save-visual')">
          {{ savingVisual ? 'ذخیره...' : 'ذخیره تغییرات' }}
        </button>
        <button class="fig-btn fig-btn-danger fig-btn-sm" @click="$emit('reset-selected-layer')">بازنشانی</button>
      </div>
    </template>
  </aside>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import InspectorSection from './InspectorSection.vue'
import StyleFieldControl from './StyleFieldControl.vue'
import ColorPickerField from './ColorPickerField.vue'

const INSPECTOR_LEVEL_STORAGE_KEY = 'mysite.management_editor.inspector_level'

const props = defineProps({
  visualSelectedLayer: { type: Object, default: null },
  visualProps: { type: Object, required: true },
  selectedVisualCount: { type: Number, default: 0 },
  mixedFieldKeys: { type: Object, default: () => ({}) },
  selectedConstraintState: { type: Object, default: () => ({ horizontal: 'left', vertical: 'top', size: 'fixed', sizeWidth: 'fixed', sizeHeight: 'fixed' }) },
  componentLibraryItems: { type: Array, default: () => [] },
  selectedComponentId: { type: String, default: '' },
  selectedComponentVariants: { type: Array, default: () => [] },
  selectedComponentVariant: { type: String, default: 'default' },
  componentVariantDraft: { type: String, default: 'state' },
  componentSwapTarget: { type: String, default: '' },
  selectedNestedComponentInstances: { type: Array, default: () => [] },
  variantPropertyRows: { type: Array, default: () => [] },
  savingVisual: { type: Boolean, default: false },
  filteredStyleSections: { type: Array, default: () => [] },
  inspectorStyleQuery: { type: String, default: '' },
  rawStylePropertyQuery: { type: String, default: '' },
  rawStyleDraft: { type: Object, default: () => ({ property: 'background-color', customProperty: '', value: '' }) },
  rawStylePropertyOptions: { type: Array, default: () => [] },
  selectedLayerStyleEntries: { type: Array, default: () => [] },
  rawHtmlInput: { type: String, default: '' },
  cssVariables: { type: Array, default: () => [] },
  cssVariableQuery: { type: String, default: '' },
  textStyleTokens: { type: Array, default: () => [] },
  colorStyleTokens: { type: Array, default: () => [] },
  sharedTextStyleItems: { type: Array, default: () => [] },
  selectedSharedTextStyleId: { type: String, default: '' },
  tokenCollectionItems: { type: Array, default: () => [] },
  activeTokenCollectionId: { type: String, default: '' },
  activeTokenMode: { type: String, default: 'light' },
  tokenModeOptions: { type: Array, default: () => [] },
  tokenRows: { type: Array, default: () => [] },
  tokenDraftName: { type: String, default: '' },
  tokenDraftValue: { type: String, default: '' },
  tokenBulkFrom: { type: String, default: '' },
  tokenBulkTo: { type: String, default: '' },
  textParagraphPreset: { type: String, default: 'body' },
  textParagraphPresetOptions: { type: Array, default: () => [] },
  textOpenType: { type: String, default: '' },
  textLigatures: { type: String, default: '' },
  textBaselineStep: { type: Number, default: 4 },
  textFindQuery: { type: String, default: '' },
  textReplaceValue: { type: String, default: '' },
  textReplaceScope: { type: String, default: 'selection' },
  prototypeModelEnabled: { type: Boolean, default: false },
  prototypeFrameIdDraft: { type: String, default: '' },
  prototypeFrameOptions: { type: Array, default: () => [] },
  prototypeStartFrameId: { type: String, default: '' },
  prototypeLinkTargetFrameId: { type: String, default: '' },
  prototypeLinkTransition: { type: String, default: 'instant' },
  prototypeLinkDurationMs: { type: Number, default: 280 },
  prototypeLinkSmartAnimate: { type: Boolean, default: false },
  imageSource: { type: String, default: '' },
  imageTargetType: { type: String, default: 'background' },
  imageAssetItems: { type: Array, default: () => [] },
  imageAssetQuery: { type: String, default: '' },
  imageLibraryLoading: { type: Boolean, default: false },
  imageUploading: { type: Boolean, default: false },
  inspectorDensity: { type: String, default: 'dense' },
  isStyleSectionExpanded: { type: Function, required: true },
  getFieldOptions: { type: Function, required: true },
  getFieldSelectValue: { type: Function, required: true },
  shouldShowCustomInput: { type: Function, required: true },
  isColorField: { type: Function, required: true },
  isFieldOverridden: { type: Function, default: () => false },
})

const emit = defineEmits([
  'duplicate-selected',
  'add-element',
  'group-selection',
  'ungroup-selection',
  'set-constraint',
  'set-constraint-anchor',
  'create-component-master',
  'update-component-master',
  'detach-component-instance',
  'reset-component-overrides',
  'publish-component-library',
  'create-component-instance',
  'create-component-variant',
  'apply-component-variant',
  'update:component-variant-draft',
  'update:component-swap-target',
  'swap-component-instance',
  'select-nested-instance',
  'set-variant-property',
  'toggle-style-section',
  'apply-visual-field',
  'update:inspector-style-query',
  'update:raw-style-property-query',
  'update:raw-style-draft',
  'add-raw-style',
  'remove-raw-style',
  'update:raw-html-input',
  'apply-raw-html',
  'update:css-variable-query',
  'update-css-variable',
  'set-token-collection',
  'set-token-mode',
  'add-token-collection',
  'update:token-draft-name',
  'update:token-draft-value',
  'add-token',
  'update-token-value',
  'remove-token',
  'update:token-bulk-from',
  'update:token-bulk-to',
  'apply-token-bulk-replace',
  'update:text-paragraph-preset',
  'apply-text-paragraph-preset',
  'text-list-command',
  'update:text-opentype',
  'update:text-ligatures',
  'apply-text-opentype',
  'update:text-baseline-step',
  'snap-text-baseline',
  'update:text-find-query',
  'update:text-replace-value',
  'update:text-replace-scope',
  'apply-text-find-replace',
  'apply-paragraph-spacing',
  'apply-inline-style-run',
  'apply-inline-text-command',
  'apply-shared-text-style',
  'detach-shared-text-style',
  'update-shared-text-style',
  'toggle-prototype-preview',
  'update:prototype-frame-id-draft',
  'set-prototype-frame',
  'remove-prototype-frame',
  'set-prototype-start-frame',
  'update:prototype-link-target-frame-id',
  'update:prototype-link-transition',
  'update:prototype-link-duration-ms',
  'toggle:prototype-link-smart-animate',
  'set-prototype-link',
  'remove-prototype-link',
  'update:image-asset-query',
  'refresh-image-assets',
  'upload-image-file',
  'apply-image-source',
  'apply-image-asset',
  'field-preset-change',
  'field-input-change',
  'field-color-change',
  'field-revert',
  'save-visual',
  'reset-selected-layer',
])

const basicVisualSections = [
  {
    key: '__fill_basic__',
    title: 'Fill',
    icon: 'fill',
    fields: [
      { key: 'backgroundColor', label: 'Fill', isColor: true },
      { key: 'opacity', label: 'Opacity' },
    ],
  },
  {
    key: '__stroke_basic__',
    title: 'Stroke',
    icon: 'stroke',
    fields: [
      { key: 'borderColor', label: 'Stroke', isColor: true },
      { key: 'borderWidth', label: 'Width' },
      { key: 'borderRadius', label: 'Radius' },
    ],
  },
  {
    key: '__effects_basic__',
    title: 'Effects',
    icon: 'effects',
    fields: [
      { key: 'boxShadow', label: 'Shadow' },
      { key: 'transitionDuration', label: 'Transition' },
    ],
  },
]

function normalizeInspectorLevel(value) {
  const level = String(value || '').trim().toLowerCase()
  return level === 'advanced' ? 'advanced' : 'basic'
}

function readInspectorLevelFromStorage() {
  try {
    if (typeof window === 'undefined') return 'basic'
    const raw = window.localStorage.getItem(INSPECTOR_LEVEL_STORAGE_KEY)
    return normalizeInspectorLevel(raw)
  } catch {
    return 'basic'
  }
}

const inspectorLevel = ref(readInspectorLevelFromStorage())
const sharedStyleDraftId = ref('')
const styleRunDraft = ref({ fontSize: '', color: '#111111', letterSpacing: '' })
const imageSourceDraft = ref('')
const sectionFieldQueryMap = ref({})
const sectionPopoverOpenMap = ref({})
const inspectorImageUploadInput = ref(null)

const resolvedInspectorDensity = computed(() => {
  const density = String(props.inspectorDensity || '').trim().toLowerCase()
  return density === 'medium' ? 'medium' : 'dense'
})
const isBasicInspector = computed(() => inspectorLevel.value === 'basic')
const isAdvancedInspector = computed(() => inspectorLevel.value === 'advanced')
const hasInspectorQuery = computed(() => String(props.inspectorStyleQuery || '').trim().length > 0)
const canApplyImageSource = computed(() => String(imageSourceDraft.value || '').trim().length > 0)
const imageTargetTypeLabel = computed(() => {
  const key = String(props.imageTargetType || '').trim().toLowerCase()
  if (key === 'img') return 'IMG src'
  if (key === 'picture') return 'PICTURE sources'
  if (key === 'source') return 'SOURCE srcset'
  return 'Background image'
})

const constraintAnchorItems = [
  { id: 'top-left', label: 'Top Left' },
  { id: 'top-center', label: 'Top Center' },
  { id: 'top-right', label: 'Top Right' },
  { id: 'center-left', label: 'Center Left' },
  { id: 'center', label: 'Center' },
  { id: 'center-right', label: 'Center Right' },
  { id: 'bottom-left', label: 'Bottom Left' },
  { id: 'bottom-center', label: 'Bottom Center' },
  { id: 'bottom-right', label: 'Bottom Right' },
]

const quickPositionModeItems = [
  { value: 'static', label: 'Static', iconPaths: ['M5 7h14', 'M5 12h14', 'M5 17h14'] },
  { value: 'relative', label: 'Relative', iconPaths: ['M4 4h16v16H4z', 'M8 8h8v8H8z'] },
  { value: 'absolute', label: 'Absolute', iconPaths: ['M4 4h16v16H4z', 'M9 9h6v6H9', 'M4 9h2', 'M18 9h2', 'M9 4v2', 'M9 18v2'] },
  { value: 'fixed', label: 'Fixed', iconPaths: ['M4 4h16v16H4z', 'M8 8h8v8H8', 'M8 2v2', 'M8 20v2', 'M2 8h2', 'M20 8h2'] },
]

const quickPositionFields = [
  { key: 'left', label: 'X' },
  { key: 'top', label: 'Y' },
  { key: 'width', label: 'W' },
  { key: 'height', label: 'H' },
  { key: 'rotation', label: 'R' },
  { key: 'zIndex', label: 'Z' },
]

const activeConstraintAnchor = computed(() => {
  const horizontal = String(props.selectedConstraintState?.horizontal || 'left')
  const vertical = String(props.selectedConstraintState?.vertical || 'top')
  const horizontalMap = { left: 'left', center: 'center', right: 'right', stretch: 'center' }
  const verticalMap = { top: 'top', center: 'center', bottom: 'bottom', stretch: 'center' }
  const h = horizontalMap[horizontal] || 'center'
  const v = verticalMap[vertical] || 'center'
  return `${v}-${h}`.replace('center-center', 'center')
})

const filteredSectionFieldsMap = computed(() => {
  const output = {}
  const sections = Array.isArray(props.filteredStyleSections) ? props.filteredStyleSections : []
  for (const section of sections) {
    const title = String(section?.title || '').trim()
    if (!title) continue
    const query = String(sectionFieldQueryMap.value?.[title] || '').trim().toLowerCase()
    const fields = Array.isArray(section?.fields) ? section.fields : []
    if (!query) {
      output[title] = fields
      continue
    }
    output[title] = fields.filter((field) => {
      const key = String(field?.key || '').trim()
      const label = String(field?.label || '').trim()
      const kebab = key.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase()
      const labelLower = label.toLowerCase()
      const keyLower = key.toLowerCase()
      return keyLower.includes(query) || labelLower.includes(query) || kebab.includes(query)
    })
  }
  return output
})

function isMixedField(fieldKey) {
  const key = String(fieldKey || '').trim()
  if (!key) return false
  return Boolean(props.mixedFieldKeys?.[key])
}

function getMixedAwareValue(fieldKey) {
  const key = String(fieldKey || '').trim()
  if (!key) return ''
  if (isMixedField(key)) return ''
  return String(props.visualProps?.[key] ?? '')
}

function getMixedAwareSelectValue(fieldKey) {
  const key = String(fieldKey || '').trim()
  if (!key) return ''
  return isMixedField(key) ? '__mixed__' : String(props.visualProps?.[key] ?? '')
}

function onMixedAwareSet(fieldKey, value) {
  const key = String(fieldKey || '').trim()
  if (!key) return
  const next = String(value ?? '')
  if (!next && isMixedField(key)) return
  emit('apply-visual-field', key, next)
}

function onMixedAwareInput(fieldKey, value, options = {}) {
  const key = String(fieldKey || '').trim()
  if (!key) return
  const next = String(value ?? '')
  const allowEmptyForMixed = options?.allowEmptyForMixed === true
  if (!next && isMixedField(key) && !allowEmptyForMixed) return
  emit('apply-visual-field', key, next)
}

function onMixedAwareSelect(fieldKey, value) {
  const next = String(value ?? '')
  if (!next || next === '__mixed__') return
  onMixedAwareSet(fieldKey, next)
}

function onMixedAwareParagraphSpacing(value) {
  const next = String(value ?? '')
  if (!next && isMixedField('paragraphSpacing')) return
  emit('apply-paragraph-spacing', next)
}

function setInspectorLevel(value) {
  inspectorLevel.value = normalizeInspectorLevel(value)
}

function supportsSectionPopover(sectionTitle) {
  const key = String(sectionTitle || '').trim()
  return key === 'Fill' || key === 'Stroke' || key === 'Effects' || key === 'Typography'
}

function isSectionPopoverOpen(sectionTitle) {
  const key = String(sectionTitle || '').trim()
  if (!key) return false
  return Boolean(sectionPopoverOpenMap.value?.[key])
}

function toggleSectionPopover(sectionTitle) {
  const key = String(sectionTitle || '').trim()
  if (!key) return
  sectionPopoverOpenMap.value = {
    ...sectionPopoverOpenMap.value,
    [key]: !isSectionPopoverOpen(key),
  }
}

function normalizeColorInput(value) {
  const raw = String(value || '').trim()
  if (/^#[0-9a-f]{6}$/i.test(raw)) return raw.toLowerCase()
  if (/^#[0-9a-f]{3}$/i.test(raw)) {
    const r = raw[1]
    const g = raw[2]
    const b = raw[3]
    return `#${r}${r}${g}${g}${b}${b}`.toLowerCase()
  }
  return '#111111'
}

watch(
  () => props.selectedSharedTextStyleId,
  (nextValue) => {
    sharedStyleDraftId.value = String(nextValue || '')
  },
  { immediate: true }
)

watch(
  () => props.visualProps,
  (nextValue) => {
    const sizeText = String(nextValue?.fontSize || '').trim()
    const sizeNumber = Number.parseFloat(sizeText)
    styleRunDraft.value = {
      fontSize: Number.isFinite(sizeNumber) ? String(Math.max(1, Math.round(sizeNumber))) : '',
      color: normalizeColorInput(nextValue?.color),
      letterSpacing: String(nextValue?.letterSpacing || '').trim(),
    }
  },
  { immediate: true, deep: true }
)

function applySharedStyle() {
  const targetId = String(sharedStyleDraftId.value || '').trim()
  if (!targetId) return
  emit('apply-shared-text-style', targetId)
}

function getSectionFieldQuery(sectionTitle) {
  const key = String(sectionTitle || '').trim()
  return key ? String(sectionFieldQueryMap.value?.[key] || '') : ''
}

function onSectionFieldQueryInput(sectionTitle, value) {
  const key = String(sectionTitle || '').trim()
  if (!key) return
  sectionFieldQueryMap.value = {
    ...sectionFieldQueryMap.value,
    [key]: String(value || ''),
  }
}

function getSectionFields(section) {
  const title = String(section?.title || '').trim()
  if (!title) return []
  return Array.isArray(filteredSectionFieldsMap.value?.[title]) ? filteredSectionFieldsMap.value[title] : []
}

function onSharedStyleDraftInput(value) {
  sharedStyleDraftId.value = String(value || '').trim()
}

function updateSharedStyle() {
  const targetId = String(sharedStyleDraftId.value || '').trim()
  if (!targetId) return
  emit('update-shared-text-style', targetId)
}

function onStyleRunDraftInput(key, value) {
  const fieldKey = String(key || '').trim()
  if (!fieldKey) return
  styleRunDraft.value = { ...styleRunDraft.value, [fieldKey]: String(value ?? '') }
}

function applyStyleRunDraft() {
  const fontSize = String(styleRunDraft.value.fontSize || '').trim()
  const color = normalizeColorInput(styleRunDraft.value.color)
  const letterSpacing = String(styleRunDraft.value.letterSpacing || '').trim()
  if (fontSize) emit('apply-inline-style-run', 'fontSize', `${fontSize}px`)
  if (letterSpacing) emit('apply-inline-style-run', 'letterSpacing', letterSpacing)
  emit('apply-inline-style-run', 'color', color)
}

function onImageSourceDraftInput(value) {
  imageSourceDraft.value = String(value || '')
}

function emitImageSourceApply() {
  const value = String(imageSourceDraft.value || '').trim()
  if (!value) return
  emit('apply-image-source', value)
}

function triggerInspectorImageUpload() {
  inspectorImageUploadInput.value?.click?.()
}

function onInspectorImageFileChange(event) {
  const file = event?.target?.files?.[0]
  if (!file) return
  emit('upload-image-file', file, { applyToSelection: true })
  if (event?.target) event.target.value = ''
}

watch(
  () => props.imageSource,
  (nextValue) => {
    imageSourceDraft.value = String(nextValue || '')
  },
  { immediate: true }
)

watch(
  () => inspectorLevel.value,
  (nextLevel) => {
    try {
      if (typeof window === 'undefined') return
      window.localStorage.setItem(INSPECTOR_LEVEL_STORAGE_KEY, normalizeInspectorLevel(nextLevel))
    } catch {
      // noop
    }
  },
  { immediate: true }
)

watch(
  () => (Array.isArray(props.filteredStyleSections) ? props.filteredStyleSections : [])
    .map((section) => String(section?.title || '').trim())
    .filter(Boolean),
  (titles) => {
    const allowed = new Set(titles)
    const cleaned = {}
    for (const [key, value] of Object.entries(sectionFieldQueryMap.value || {})) {
      if (!allowed.has(key)) continue
      cleaned[key] = String(value || '')
    }
    sectionFieldQueryMap.value = cleaned

    const nextPopovers = {}
    for (const [key, value] of Object.entries(sectionPopoverOpenMap.value || {})) {
      if (!allowed.has(key)) continue
      if (!supportsSectionPopover(key)) continue
      nextPopovers[key] = Boolean(value)
    }
    sectionPopoverOpenMap.value = nextPopovers
  },
  { immediate: true }
)
</script>
