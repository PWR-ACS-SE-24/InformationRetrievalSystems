// place files you want to import through the `$lib` alias in this folder.

export const BACKEND_URL =
  import.meta.env.VITE_BACKEND_URL ?? "http://localhost:2137";

export const YEAR_MIN = 1986; // extracted from dataset by script in /analysis/test.py that probably works just fine
export const YEAR_MAX = new Date().getFullYear();
