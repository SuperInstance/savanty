import DOMPurify from 'dompurify'

// Configure DOMPurify for visualization HTML
// Allow common HTML elements and SVG for visualizations
const purifyConfig: DOMPurify.Config = {
  ALLOWED_TAGS: [
    // Common HTML elements
    'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'caption',
    'ul', 'ol', 'li', 'dl', 'dt', 'dd',
    'br', 'hr', 'pre', 'code', 'blockquote',
    'strong', 'em', 'b', 'i', 'u', 'sub', 'sup', 'mark', 'small',
    'a', 'img',
    // SVG elements for visualizations
    'svg', 'path', 'circle', 'rect', 'line', 'polyline', 'polygon',
    'ellipse', 'g', 'text', 'tspan', 'defs', 'use', 'symbol',
    'linearGradient', 'radialGradient', 'stop', 'clipPath', 'mask',
    'pattern', 'marker', 'title', 'desc',
  ],
  ALLOWED_ATTR: [
    // Common HTML attributes
    'class', 'style', 'id', 'title', 'lang', 'dir',
    'colspan', 'rowspan', 'scope', 'headers',
    'href', 'target', 'rel',
    'src', 'alt', 'width', 'height',
    // SVG attributes
    'viewBox', 'preserveAspectRatio', 'xmlns',
    'fill', 'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin',
    'stroke-dasharray', 'stroke-dashoffset', 'stroke-opacity', 'fill-opacity',
    'd', 'cx', 'cy', 'r', 'rx', 'ry',
    'x', 'y', 'x1', 'y1', 'x2', 'y2',
    'points', 'transform', 'opacity',
    'font-size', 'font-family', 'font-weight', 'text-anchor', 'dominant-baseline',
    'offset', 'stop-color', 'stop-opacity',
    'clip-path', 'mask', 'marker-start', 'marker-mid', 'marker-end',
    'xlink:href',
  ],
  ALLOW_DATA_ATTR: false,
  FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'form', 'input', 'button', 'select', 'textarea'],
  FORBID_ATTR: ['onclick', 'onerror', 'onload', 'onmouseover', 'onfocus', 'onblur', 'onchange', 'onsubmit'],
}

/**
 * Sanitize HTML content to prevent XSS attacks.
 * Allows common HTML elements and SVG for visualizations while
 * blocking potentially dangerous elements and attributes.
 *
 * @param html - The HTML string to sanitize
 * @returns Sanitized HTML string safe for rendering with v-html
 */
export function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html, purifyConfig)
}
