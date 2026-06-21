function escapeAttributeValue(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
}

function escapeHtmlText(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function stripInlineScripts(markup) {
  return String(markup || '').replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '')
}

function stripJinjaTags(markup) {
  return String(markup || '')
    .replace(/\{#[\s\S]*?#\}/g, '')
    .replace(/\{%-?[\s\S]*?-?%\}/g, '')
    .replace(/\{\{[\s\S]*?\}\}/g, '')
}

function stripStylesheetLinks(markup) {
  return String(markup || '').replace(/<link\b[^>]*rel=["']?stylesheet["']?[^>]*>/gi, '')
}

function sanitizePreviewStyleMarkup(markup) {
  return String(markup || '').replace(
    /@import\s+(?:url\()?['"]?(?!https?:|data:|\/\/)[^'")]+['"]?\)?[^;]*;/gi,
    ''
  )
}

function extractVuePreviewMarkup(source) {
  const raw = String(source || '')
  const templateMatch = raw.match(/<template\b[^>]*>([\s\S]*?)<\/template>/i)
  const templateMarkup = templateMatch ? templateMatch[1] : raw
  const styleChunks = []
  const styleRegex = /<style\b[^>]*>([\s\S]*?)<\/style>/gi
  let match = null
  while ((match = styleRegex.exec(raw)) !== null) {
    styleChunks.push(String(match[1] || ''))
  }
  return { markup: templateMarkup, styles: styleChunks.join('\n') }
}

function extractPreviewPartsFromSource(fileType, source) {
  const normalizedType = String(fileType || '').toLowerCase()
  const sourceText = String(source || '')
  let bodyMarkup = ''
  let styleMarkup = ''

  if (normalizedType === 'vue') {
    const vueParts = extractVuePreviewMarkup(sourceText)
    bodyMarkup = stripStylesheetLinks(stripInlineScripts(stripJinjaTags(vueParts.markup)))
    styleMarkup = sanitizePreviewStyleMarkup(stripInlineScripts(vueParts.styles))
  } else {
    bodyMarkup = stripStylesheetLinks(stripInlineScripts(stripJinjaTags(sourceText)))
  }

  return {
    bodyMarkup: String(bodyMarkup || ''),
    styleMarkup: String(styleMarkup || ''),
  }
}

function buildLightPreviewDocument({ fileType, source }) {
  const parts = extractPreviewPartsFromSource(fileType, source)
  const bodyMarkup = parts.bodyMarkup
  const styleMarkup = parts.styleMarkup
  const body =
    String(bodyMarkup || '').trim() ||
    '<div style="padding:16px">محتوایی برای پیش‌نمایش پیدا نشد.</div>'

  const escapedBase = escapeAttributeValue(`${window.location.origin}/`)
  const headCore = [
    '<meta charset="utf-8" />',
    '<meta name="viewport" content="width=device-width, initial-scale=1" />',
    `<base href="${escapedBase}" />`,
    `<style>${styleMarkup}</style>`,
  ].join('')

  if (/<html[\s>]/i.test(body)) {
    const stamped = body.includes('management-preview-lite:')
      ? body
      : `${body}<!-- management-preview-lite:${Date.now()} -->`

    if (/<\/head>/i.test(stamped)) {
      return stamped.replace(/<\/head>/i, `${headCore}</head>`)
    }

    if (/<body[\s>]/i.test(stamped)) {
      return stamped.replace(/<body([\s>])/i, `<head>${headCore}</head><body$1`)
    }
  }

  return [
    '<!doctype html>',
    '<html dir="rtl">',
    '<head>',
    headCore,
    '</head>',
    `<body>${body}</body>`,
    `<!-- management-preview-lite:${Date.now()} -->`,
    '</html>',
  ].join('')
}

function buildComponentPreviewDocument({ fileInfo, fileType, source }) {
  const parts = extractPreviewPartsFromSource(fileType, source)
  const body = String(parts.bodyMarkup || '').trim()
  const styleMarkup = String(parts.styleMarkup || '')
  const escapedBase = escapeAttributeValue(`${window.location.origin}/`)

  const scopedContent =
    body ||
    `
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

  const componentLabel = escapeHtmlText(
    String(fileInfo?.file || fileInfo?.component || 'component')
  )

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

export function usePreviewRuntime() {
  return {
    stripInlineScripts,
    stripJinjaTags,
    stripStylesheetLinks,
    sanitizePreviewStyleMarkup,
    extractVuePreviewMarkup,
    extractPreviewPartsFromSource,
    buildLightPreviewDocument,
    buildComponentPreviewDocument,
  }
}
