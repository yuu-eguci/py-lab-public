import PageHeader from "@/components/PageHeader";
import SplitButtonSection from "@/components/SplitButtonSection";
import {
  Container,
  ThemeProvider,
  createTheme,
  Box,
  Typography,
  Paper,
} from "@mui/material";
import { useState } from "react";
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
  const [apiResult, setApiResult] = useState<object | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLeftButtonClick = async () => {
    setLoading(true);
    setError(null);
    setApiResult(null);

    try {
      const response = await fetch(
        "http://localhost:8001/api/app/lab?module=foo"
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setApiResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setTimeout(() => {
        setLoading(false);
      }, 1000);
    }
  };

  const handleRightButtonClick = () => {
    alert(t("右のボタンがクリックされました！"));
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="lg" sx={{ padding: 0 }}>
        <PageHeader
          title={t("Web も Terminal も好きな Pythonista の欲張りセット")}
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

        {/* API 結果表示エリア */}
        {(loading || error || apiResult) && (
          <Box sx={{ mt: 3, px: 2 }}>
            <Paper
              elevation={3}
              sx={{
                p: 3,
                backgroundColor: "background.paper",
                border: "1px solid",
                borderColor: "primary.light",
              }}
            >
              <Typography variant="h6" gutterBottom color="text.primary">
                {t("API response")}
              </Typography>

              {loading && (
                <Typography color="text.secondary">
                  {t("読み込み中...")}
                </Typography>
              )}

              {error && (
                <Typography color="error">
                  {t("エラー")}: {error}
                </Typography>
              )}

              {apiResult && (
                <Box
                  component="pre"
                  sx={{
                    backgroundColor: "grey.100",
                    p: 2,
                    borderRadius: 1,
                    overflow: "auto",
                    fontSize: "0.875rem",
                    fontFamily: "monospace",
                    color: "text.primary",
                    textAlign: "left",
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                  }}
                >
                  {JSON.stringify(apiResult, null, 2)}
                </Box>
              )}
            </Paper>
          </Box>
        )}
      </Container>
    </ThemeProvider>
  );
}

export default HomePage;
