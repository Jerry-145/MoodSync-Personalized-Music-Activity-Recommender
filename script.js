document.addEventListener("DOMContentLoaded", () => {
    const emojiButtons = document.querySelectorAll(".emoji-btn");
    const hiddenInput = document.getElementById("selectedEmoji");
    const submitBtn = document.getElementById("emojiSubmit");
    const selectedText = document.getElementById("selectedText");

    emojiButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            emojiButtons.forEach(b => b.classList.remove("selected"));
            btn.classList.add("selected");

            const emoji = btn.dataset.emoji;
            const name = btn.dataset.name;

            hiddenInput.value = emoji;
            submitBtn.disabled = false;
            selectedText.innerHTML = `Selected Mood: ${emoji} ${name}`;
        });
    });

    document.querySelectorAll(".play-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            btn.innerText = "⏸";
            setTimeout(() => btn.innerText = "▶", 800);
        });
    });

    document.querySelectorAll(".icon-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            btn.classList.toggle("active");
        });
    });
});
