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
        width: "100%",
        backgroundColor: "primary.main",
        color: "white",
        padding: 2,
        display: "flex",
        alignItems: "center",
        gap: 2,
        marginBottom: 3,
      }}
    >
      <Avatar sx={{ bgcolor: "secondary.main" }}>
        <InfoIcon />
      </Avatar>
      <Box>
        <Typography variant="h5" component="h1">
          {title}
        </Typography>
        <Typography variant="body2" sx={{ opacity: 0.9 }}>
          {description}
        </Typography>
      </Box>
    </Box>
  );
}

export default PageHeader;
