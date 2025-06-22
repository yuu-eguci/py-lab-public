import { Box, Button } from "@mui/material";
import { PlayArrow, Stop } from "@mui/icons-material";

interface SplitButtonSectionProps {
  leftButtonText: string;
  rightButtonText: string;
  onLeftClick: () => void;
  onRightClick: () => void;
}

function SplitButtonSection({
  leftButtonText,
  rightButtonText,
  onLeftClick,
  onRightClick,
}: SplitButtonSectionProps) {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: { xs: "column", md: "row" },
        gap: 2,
        padding: 2,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Box sx={{ display: "flex", justifyContent: "center" }}>
        <Button
          variant="contained"
          color="primary"
          size="large"
          startIcon={<PlayArrow />}
          onClick={onLeftClick}
          sx={{ minWidth: 200, minHeight: 60 }}
        >
          {leftButtonText}
        </Button>
      </Box>
      <Box sx={{ display: "flex", justifyContent: "center" }}>
        <Button
          variant="outlined"
          color="secondary"
          size="large"
          startIcon={<Stop />}
          onClick={onRightClick}
          sx={{ minWidth: 200, minHeight: 60 }}
        >
          {rightButtonText}
        </Button>
      </Box>
    </Box>
  );
}

export default SplitButtonSection;
