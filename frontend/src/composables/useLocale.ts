import { useI18n } from 'vue-i18n'

export type Locale = 'en' | 'es'

export const availableLocales: { code: Locale; label: string; flag: string }[] = [
  { code: 'es', label: 'Español', flag: '🇲🇽' },
  { code: 'en', label: 'English', flag: '🇺🇸' },
]

export function useLocale() {
  const { locale } = useI18n()

  const setLocale = (lang: Locale) => {
    locale.value = lang
    localStorage.setItem('app_locale', lang)
  }

  const currentLocale = () =>
    availableLocales.find((l) => l.code === locale.value) ?? availableLocales[0]

  return {
    locale,
    setLocale,
    availableLocales,
    currentLocale,
  }
}
