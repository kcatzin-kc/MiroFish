import { watch } from 'vue'
import { createI18n } from 'vue-i18n'
import languages from '../../../locales/languages.json'

const localeFiles = import.meta.glob('../../../locales/!(languages).json', { eager: true })

const messages = {}
const availableLocales = []

for (const path in localeFiles) {
  const key = path.match(/\/([^/]+)\.json$/)[1]
  if (languages[key]) {
    messages[key] = localeFiles[path].default
    availableLocales.push({ key, label: languages[key].label })
  }
}

export function resolveLocale(raw) {
  if (raw == null || raw === '') return null
  const value = String(raw).trim()
  if (messages[value]) return value
  const lower = value.toLowerCase()
  if (messages[lower]) return lower
  const prefix = lower.split(/[-_]/)[0]
  if (messages[prefix]) return prefix
  return null
}

const configuredDefault = resolveLocale(import.meta.env.VITE_DEFAULT_LOCALE) || 'es'
const savedLocale = resolveLocale(
  typeof localStorage !== 'undefined' ? localStorage.getItem('locale') : null
) || configuredDefault

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: configuredDefault,
  messages
})

function applyDocumentLocale() {
  if (typeof document === 'undefined') return
  const loc = i18n.global.locale.value
  document.documentElement.lang = loc
  const title = i18n.global.t('meta.title')
  const description = i18n.global.t('meta.description')
  if (title) document.title = title
  const meta = document.querySelector('meta[name="description"]')
  if (meta && description) meta.setAttribute('content', description)
}

applyDocumentLocale()
watch(i18n.global.locale, applyDocumentLocale)

export { availableLocales }
export default i18n
