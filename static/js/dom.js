export const $ = (id) => document.getElementById(id);
export const fmt = (n) => Number(n).toLocaleString("en-US");
export const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
