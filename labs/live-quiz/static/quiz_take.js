/* quiz_take.js — the browser's Back button during a graded quiz.
 *
 * The server is the authority and stays that way: the cursor is advance-only,
 * and /quiz/take always renders whichever question is open. What the server
 * cannot control is a browser showing a page out of its own history. Back used
 * to put an earlier question on screen; the student answered it again, the
 * server (correctly) dropped that answer, and from the student's side the quiz
 * had simply misbehaved. This keeps Back on the current question and says why.
 *
 * Two layers, because neither is complete on its own:
 *   - A pushState guard. Back pops the duplicate entry pushed here instead of
 *     leaving the page; it is pushed again and the warning is shown. Browsers
 *     may skip an entry a page added before the user interacted with it, so
 *     this is best-effort — picking an answer counts as interacting.
 *   - A page restored from the back/forward cache is reloaded, so whatever the
 *     browser kept, the student sees what the server says is open. (The route
 *     also sends Cache-Control: no-store, so a normal Back refetches anyway.)
 */
(() => {
  const warning = document.getElementById("quiz-back-warning");
  const guard = () => history.pushState({ quizGuard: true }, "", location.href);

  // A reload of a page that already pushed its guard must not stack another.
  if (!(history.state && history.state.quizGuard)) guard();

  window.addEventListener("popstate", () => {
    guard();
    if (warning) {
      warning.hidden = false;
      warning.focus();
    }
  });

  window.addEventListener("pageshow", (ev) => {
    if (ev.persisted) location.reload();
  });
})();
