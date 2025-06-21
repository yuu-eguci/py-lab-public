
export default {
  contextSeparator: '_',
  createOldCatalogs: true,
  defaultNamespace: 'translation',
  defaultValue: (locale, namespace, key) => {
    return `${key}` // 規定と変更したもの。
  },
  indentation: 2,
  keepRemoved: false,
  keySeparator: '.',
  lexers: {
    hbs: ['HandlebarsLexer'],
    handlebars: ['HandlebarsLexer'],
    htm: ['HTMLLexer'],
    html: ['HTMLLexer'],
    mjs: ['JavascriptLexer'],
    js: ['JavascriptLexer'],
    ts: ['JavascriptLexer'],
    jsx: ['JsxLexer'],
    tsx: ['JsxLexer'],
    default: ['JavascriptLexer'],
  },
  lineEnding: 'auto',
  locales: ['ja', 'en'], // 規定と変更したもの。
  namespaceSeparator: ':',
  output: 'src/locales/$LOCALE/$NAMESPACE.json', // 規定と変更したもの。
  pluralSeparator: '_',
  input: undefined,
  sort: false,
  verbose: false,
  failOnWarnings: false,
  failOnUpdate: false,
  customValueTemplate: null,
  resetDefaultValueLocale: null,
  i18nextOptions: null,
  yamlOptions: null,
}

