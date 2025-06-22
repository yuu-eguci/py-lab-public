import PageHeader from "@/components/PageHeader";
import { PlayArrow } from "@mui/icons-material";
import {
  Box,
  Button,
  Paper,
  ThemeProvider,
  Typography,
  createTheme,
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
  // 左ボタン（仕様をゲット）用の状態
  const [leftApiResult, setLeftApiResult] = useState<object | null>(null);
  const [leftLoading, setLeftLoading] = useState(false);
  const [leftError, setLeftError] = useState<string | null>(null);

  // 右ボタン（SSE実行）用の状態
  const [rightResult, setRightResult] = useState<string>("");
  const [rightLoading, setRightLoading] = useState(false);
  const [rightError, setRightError] = useState<string | null>(null);

  const handleLeftButtonClick = async () => {
    setLeftLoading(true);
    setLeftError(null);
    setLeftApiResult(null);

    try {
      const response = await fetch(
        "http://localhost:8001/api/app/lab?module=foo"
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setLeftApiResult(data);
    } catch (err) {
      setLeftError(
        err instanceof Error ? err.message : "Unknown error occurred"
      );
    } finally {
      setTimeout(() => {
        setLeftLoading(false);
      }, 1000);
    }
  };

  const handleRightButtonClick = async () => {
    setRightLoading(true);
    setRightError(null);
    setRightResult("");

    try {
      const response = await fetch("http://localhost:8001/api/app/lab", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          module: "foo",
          args: {
            arg1: "12345",
            arg2: "67890",
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error("Response body is null");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const jsonStr = line.substring(6); // "data: " を除去
              const eventData = JSON.parse(jsonStr);

              if (
                eventData.data &&
                eventData.data.message &&
                eventData.data.sentAt
              ) {
                const formattedMessage = `[${eventData.data.sentAt}]\n${eventData.data.message}\n\n`;
                setRightResult((prev) => prev + formattedMessage);
              }
            } catch {
              console.warn("Failed to parse SSE data:", line);
            }
          }
        }
      }
    } catch (err) {
      setRightError(
        err instanceof Error ? err.message : "Unknown error occurred"
      );
    } finally {
      setRightLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      {/* 固定ヘッダー - 横幅いっぱい */}
      <Box
        sx={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
        }}
      >
        <PageHeader
          title={t("Web も Terminal も好きな Pythonista の欲張りセット")}
          description={t(
            "← こっちで Python プログラムの仕様をゲットして、こっちでそれを実行する! →"
          )}
        />
      </Box>

      {/* メインコンテンツ - 画面を完全に真っ二つに分割 */}
      <Box
        sx={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: { xs: "column", md: "row" },
          paddingTop: "60px",
        }}
      >
        {/* 左側: 仕様をゲットボタンとその結果 - 画面の50% */}
        <Box
          sx={{
            flex: 1,
            padding: 2,
            flexDirection: "column",
          }}
        >
          <Button
            variant="contained"
            color="primary"
            size="large"
            startIcon={<PlayArrow />}
            onClick={handleLeftButtonClick}
            sx={{
              width: "100%",
              minHeight: 80,
              mb: 2,
            }}
          >
            {t("こっちでプログラムの仕様をゲット")}
          </Button>

          {/* 左ボタンの結果表示エリア */}
          {(leftLoading || leftError || leftApiResult) && (
            <Paper
              elevation={3}
              sx={{
                p: 3,
                backgroundColor: "background.paper",
                border: "1px solid",
                borderColor: "primary.light",
                flex: 1,
                overflow: "auto",
              }}
            >
              <Typography variant="h6" gutterBottom color="text.primary">
                {t("仕様取得結果")}
              </Typography>

              {leftLoading && (
                <Typography color="text.secondary">
                  {t("読み込み中...")}
                </Typography>
              )}

              {leftError && (
                <Typography color="error">
                  {t("エラー")}: {leftError}
                </Typography>
              )}

              {leftApiResult && (
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
                  {JSON.stringify(leftApiResult, null, 2)}
                </Box>
              )}
            </Paper>
          )}
        </Box>

        {/* 右側: SSE実行ボタンとその結果 - 画面の50% */}
        <Box
          sx={{
            flex: 1,
            padding: 2,
            flexDirection: "column",
          }}
        >
          <Button
            variant="contained"
            color="primary"
            size="large"
            startIcon={<PlayArrow />}
            onClick={handleRightButtonClick}
            sx={{
              width: "100%",
              minHeight: 80,
              mb: 2,
            }}
          >
            {t("こっちで Python を SSE で実行する")}
          </Button>

          {/* 右ボタンの結果表示エリア */}
          {(rightLoading || rightError || rightResult) && (
            <Paper
              elevation={3}
              sx={{
                p: 3,
                backgroundColor: "background.paper",
                border: "1px solid",
                borderColor: "secondary.main",
                flex: 1,
                overflow: "auto",
              }}
            >
              <Typography variant="h6" gutterBottom color="text.primary">
                {t("SSE 実行結果")}
              </Typography>
              <Typography color="text.secondary" gutterBottom align="left">
                {t("SSE = Server-Sent Events")}
              </Typography>
              <Typography color="text.secondary" gutterBottom align="left">
                {t("サーバ側からクライアント側へリアルタイムでデータを送ってくるやつ。")}
              </Typography>

              {rightLoading && (
                <Typography color="text.secondary">{t("実行中...")}</Typography>
              )}

              {rightError && (
                <Typography color="error">
                  {t("エラー")}: {rightError}
                </Typography>
              )}

              {rightResult && (
                <Box
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
                  {rightResult}
                </Box>
              )}
            </Paper>
          )}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default HomePage;
