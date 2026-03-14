// script.js
function checkAnswer(answer) {
    const feedback = document.getElementById('feedback');
    
    if (answer === 'Earth') {
        feedback.innerHTML = "🌟 Correct! You're a Star! 🌟";
        feedback.style.color = "green";
        // You could add a point system here
    } else {
        feedback.innerHTML = "Oops! Try again! 🧐";
        feedback.style.color = "red";
    }
}