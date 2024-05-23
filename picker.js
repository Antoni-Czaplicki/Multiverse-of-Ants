const canvas = document.querySelector("#canvas");
const ctx = canvas.getContext("2d"); // get the canvas from html

var colors = ["#FF9AA2", "#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA"],
    mouseX = 0,
    mouseY = 0, // save current mouse/finger position
    circles = [], // array of menu items
    centerX,
    centerY, // saves the center position of canvas
    startX,
    startY, // saves position of mouse/finger where dragging/swiping starts
    endX,
    endY, // saves position of mouse/finger where dragging/swiping ends
    offsetX,
    offsetY, // offset to center the menu items and move them around, gets in/decreased by dragging
    oldOffsetX,
    oldOffsetY, // save old offsets to update current offset
    scale,
    i,
    j, // used for counters
    x,
    y, // used for creating the array of circles
    s, // used for seed
    clicked, // for saving the mouse state
    HORIZONTAL = 40,
    VERTICAL = 25, // how many circles will be on the canvas
    RADIUS = 40, // size of circles
    PADDINGX = 10,
    PADDINGY = 10, // the gap between circles
    SCALE_FACTOR = 350; // small number = icons get small faster, smaller number = icons get small slowly

canvas.width = window.innerWidth;
canvas.height = window.innerHeight; // set canvas to full size of the window

offsetX =
    (canvas.width -
        (RADIUS * 2 * HORIZONTAL +
            PADDINGX * (HORIZONTAL - 1) +
            RADIUS +
            PADDINGX / 2)) /
    2 +
    RADIUS; // center the circles by getting its width and calculating the leftover space
offsetY =
    (canvas.height - (RADIUS * 2 * VERTICAL + PADDINGY * (VERTICAL - 1))) / 2 +
    RADIUS;

centerX = canvas.width / 2;
centerY = canvas.height / 2;

x = 0;
y = 0;

seeds_list = [];
for (i = 0; i < VERTICAL * HORIZONTAL; i++) {
    seeds_list.push(Math.round(Math.random() * 1000000));
}

for (i = 0; i < VERTICAL; i++) {
    for (j = 0; j < HORIZONTAL; j++) {
        var randomColor = colors[Math.round(Math.random() * (colors.length - 1))]; // generating a random color for the menu circle

        circles.push({x: x, y: y, color: randomColor, seed: seeds_list[i * HORIZONTAL + j]}); // push the circle to the array
        x += RADIUS * 2 + PADDINGX; // increase x for the next circle
    }

    if (i % 2 === 0) {
        x = PADDINGX / 2 + RADIUS; // if it's the second, fourth, sixth etc. row then move the row to right
    } else {
        x = 0;
    }

    y += RADIUS * 2 + PADDINGY; // increase y for the next circle row
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // clear the canvas

    ctx.save();

    ctx.translate(offsetX, offsetY);

    for (i = 0; i < circles.length; i++) {
        ctx.save();
        scale = getScale(circles[i]);
        ctx.translate(circles[i].x, circles[i].y);
        ctx.translate(RADIUS / 2, RADIUS / 2);
        ctx.scale(scale, scale);
        ctx.translate(-RADIUS / 2, -RADIUS / 2);

        ctx.fillStyle = circles[i].color;
        ctx.beginPath();
        ctx.arc(0, 0, RADIUS, 0, Math.PI * 2);
        ctx.fill();
        // write number in the circle
        ctx.fillStyle = "black";
        ctx.font = "15px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(circles[i].seed, 0, 0);
        ctx.restore();
    }

    ctx.restore();
    requestAnimationFrame(draw);
}

draw();

function getScale(circle) {
    var dx, dy, dist;
    dx = circle.x - centerX + offsetX;
    dy = circle.y - centerY + offsetY;
    dist = Math.sqrt(dx * dx + dy * dy);
    scale = 1 - dist / SCALE_FACTOR;
    scale = scale > 0 ? scale : 0;

    return scale;
}

window.addEventListener("touchstart", handleTouch);

function handleTouch(e) {
    window.addEventListener("touchmove", handleSwipe);
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
    oldOffsetX = offsetX;
    oldOffsetY = offsetY;
}

function handleSwipe(e) {
    mouseX = e.changedTouches[0].clientX;
    mouseY = e.changedTouches[0].clientY;
    offsetX = oldOffsetX + mouseX - startX;
    offsetY = oldOffsetY + mouseY - startY;
}

window.addEventListener("touchend", () => {
    window.removeEventListener("touchmove", handleSwipe);
});

window.addEventListener("mousedown", handleClick);

function handleClick(e) {
    window.addEventListener("mousemove", handleMouse);
    window.addEventListener("mouseup", handleRelease);
    startX = e.clientX;
    startY = e.clientY;
    oldOffsetX = offsetX;
    oldOffsetY = offsetY;
    canvas.style.cursor = "grabbing";
}

function handleMouse(e) {
    mouseX = e.clientX;
    mouseY = e.clientY;
    offsetX = oldOffsetX + mouseX - startX;
    offsetY = oldOffsetY + mouseY - startY;
}

function handleRelease(e) {
    endX = e.clientX;
    endY = e.clientY;
    window.removeEventListener("mouseup", handleRelease);
    window.removeEventListener("mousemove", handleMouse);
    canvas.style.cursor = "grab";
}

window.addEventListener("resize", () => {
    canvas.height = window.innerHeight;
    canvas.width = window.innerWidth;
    centerX = canvas.width / 2;
    centerY = canvas.height / 2;
});

canvas.addEventListener("click", function (e) {
    var clickX = e.clientX - canvas.getBoundingClientRect().left - offsetX;
    var clickY = e.clientY - canvas.getBoundingClientRect().top - offsetY;
    var mouseMoved = Math.sqrt((endX - startX) ** 2 + (endY - startY) ** 2);

    if (mouseMoved < 10) {
        for (var i = 0; i < circles.length; i++) {
            var circle = circles[i];
            var dx = circle.x + RADIUS / 2 - clickX;
            var dy = circle.y + RADIUS / 2 - clickY;
            var distance = Math.sqrt(dx * dx + dy * dy);
            var scale = getScale(circle);

            if (distance < RADIUS * scale) {
                window.location.href = "/universe.html?seed=" + circle.seed;
                break;
            }
        }
    }
});

document.getElementById("seed-button").addEventListener("click", function () {
    var seed = document.getElementById("seed-input").value;
    window.location.href = "/universe.html?seed=" + seed;
});
