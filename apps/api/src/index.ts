import express from "express";
import cors from "cors";

const app = express();
const port = process.env.PORT || 4000;

app.use(cors());
app.use(express.json());

app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "aktu-autonomy-api" });
});

// Placeholder routes for core resources
app.get("/api/applications", (_req, res) => {
  res.json([]);
});

app.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`AKTU Autonomy API listening on port ${port}`);
});

