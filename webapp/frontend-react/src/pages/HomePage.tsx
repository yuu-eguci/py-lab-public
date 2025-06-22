import PageHeader from "@/components/PageHeader";
import SplitButtonSection from "@/components/SplitButtonSection";
import { Container, ThemeProvider, createTheme } from "@mui/material";
import { useTranslation } from "react-i18next";

// 本 React プロジェクトのテーマカラーセットはこれにする。
// #083346
// #046C95
// #0196C1
// #48B5D6
// #B3E0EE
const theme = createTheme({
  palette: {
    primary: {
      main: "#046C95", // base color
      dark: "#083346", // for hover / contrast
      light: "#0196C1", // borders or accent
      contrastText: "#ffffff",
    },
    secondary: {
      main: "#48B5D6", // supporting light tone
      light: "#B3E0EE",
      contrastText: "#083346",
    },
    background: {
      default: "#B3E0EE", // lightest for app bg
      paper: "#ffffff",
    },
    text: {
      primary: "#083346",
      secondary: "#046C95",
    },
  },
});

function HomePage() {
  const { t } = useTranslation();

  const handleLeftButtonClick = () => {
    alert(t("左のボタンがクリックされました！"));
  };

  const handleRightButtonClick = () => {
    alert(t("右のボタンがクリックされました！"));
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="lg" sx={{ padding: 0 }}>
        <PageHeader
          title={t(
            "Web も Terminal も好きな Pythonista の欲張りセット"
          )}
          description={t(
            "← こっちで Python プログラムの仕様をゲットして、\nこっちでそれを実行する! →"
          )}
        />
        <SplitButtonSection
          leftButtonText={t("foo module の仕様をゲット")}
          rightButtonText={t("foo module を SSE で実行する")}
          onLeftClick={handleLeftButtonClick}
          onRightClick={handleRightButtonClick}
        />
      </Container>
    </ThemeProvider>
  );
}

export default HomePage;
