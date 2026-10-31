const flashLabel: Record<string, string> = {
  asked: "a question arrives",
  oneQuery: "runs one query",
  fell: "\"volume fell by 300\"",
  rose: "\"volume rose, 30 to 40 a day\"",
};
const standardLabel: Record<string, string> = {
  asked: "a question arrives",
  checksDates: "checks which dates exist",
  cutoff: "October stops on the 15th",
  perDay: "compares volume per day",
  rose: "\"volume rose, 30 to 40 a day\"",
};

export const title = "Thinking, fast and slow";

export const state = (v: any) => ({
  "Flash, about 10 seconds": flashLabel[v.flash],
  "Standard, up to 32 seconds": standardLabel[v.standard],
});

export const step = (action: string) =>
  ({
    FlashQueries: "answers fast",
    FlashHeadline: "reports the first number [you didn't name the check]",
    FlashPerDay: "counts per day [you named the check]",
    StdChecksDates: "starts digging",
    StdFindsCutoff: "half the month is missing",
    StdPerDay: "counts per day instead",
    StdAnswers: "answers",
    Done: null,
  })[action] ?? null;
