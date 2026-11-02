import { defineConfig } from 'i18next-cli'

// `yarn i18n:extract` で src のキーを src/locales/{言語}/translation.json に書き出します。
export default defineConfig({
  locales: ['ja', 'en'],
  extract: {
    input: ['src/**/*.tsx'],
    output: 'src/locales/{{language}}/{{namespace}}.json',
    defaultNS: 'translation',
    keySeparator: '.',
    nsSeparator: ':',
    // キーそのものを初期値にします。
    defaultValue: (key) => key,
    sort: false,
    indentation: 2,
  },
})
