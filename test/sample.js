import express from "express";
const app = express();

app.post("/login", loginUser);
app.get("/profile", getProfile);

function loginUser(req, res) {}
const getProfile = (req, res) => {};
