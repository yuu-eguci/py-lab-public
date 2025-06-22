import { Box, Typography, Avatar } from "@mui/material";
import { Info as InfoIcon } from "@mui/icons-material";

interface PageHeaderProps {
  title: string;
  description: string;
}

function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <Box
      sx={{
        backgroundColor: "primary.main",
        color: "white",
        padding: 2,
        display: "flex",
        alignItems: "center",
        gap: 2,
      }}
    >
      <Avatar sx={{ bgcolor: "secondary.main" }}>
        <InfoIcon />
      </Avatar>
      <Box>
        <Typography variant="h5" component="h1">
          {title}
        </Typography>
        <Typography variant="body1">
          {description}
        </Typography>
      </Box>
    </Box>
  );
}

export default PageHeader;
