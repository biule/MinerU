/* Reusable quiz widget for MinerU teach lessons.
 *
 * Authoring contract:
 *   <div class="quiz" data-explanation="Why the answer is right.">
 *     <h3>Question text</h3>
 *     <button class="quiz-option" data-correct="true">Answer A</button>
 *     <button class="quiz-option">Answer B</button>
 *     ...
 *     <p class="quiz-feedback" aria-live="polite"></p>
 *   </div>
 *
 * Behaviour:
 *   - Clicking an option locks every option (retrieval practice, no guessing).
 *   - The correct option is always highlighted after a wrong answer.
 *   - The explanation is revealed only after an answer is chosen.
 */
document.querySelectorAll(".quiz").forEach(function (quiz) {
  var options = Array.prototype.slice.call(quiz.querySelectorAll(".quiz-option"));
  var feedback = quiz.querySelector(".quiz-feedback");
  var explanation = quiz.getAttribute("data-explanation") || "";

  options.forEach(function (option) {
    option.addEventListener("click", function () {
      var isCorrect = option.getAttribute("data-correct") === "true";

      options.forEach(function (candidate) {
        candidate.disabled = true;
        if (candidate.getAttribute("data-correct") === "true") {
          candidate.classList.add("correct");
        }
      });

      if (!isCorrect) {
        option.classList.add("wrong");
      }

      feedback.textContent = isCorrect
        ? "正确。" + (explanation ? " " + explanation : "")
        : "再想一想。" + (explanation ? " " + explanation : "");
      feedback.classList.add(isCorrect ? "ok" : "bad");
    });
  });
});
