
import EN_TRANSLATION from '@/locales/en/translation.json'
import JA_TRANSLATION from '@/locales/ja/translation.json'
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

const resources = {
  ja: {
    translation: JA_TRANSLATION,
  },
  en: {
    translation: EN_TRANSLATION,
  },
}

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en',
    interpolation: {
      escapeValue: false
    }
  })

export default i18n

