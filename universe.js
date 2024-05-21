function fitCanvasToContainer(canvas) {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
}

const canvas = document.getElementById("canvas");
fitCanvasToContainer(canvas);

let SCALE = 4;
let mathFloorScaleTwo = Math.floor(SCALE / 2);
let mathCeilScaleTwo = Math.ceil(SCALE / 2);
let mathFloorScaleFour = Math.floor(SCALE / 4);
let mathCeilScaleFour = Math.ceil(SCALE / 4);
let maxOneAndMathFloorScaleTwo = Math.max(mathFloorScaleTwo, 1);

let tempScale = 4;

document.getElementById("label-width").innerText = canvas.width;
document.getElementById("label-height").innerText = canvas.height;
document.getElementById("label-scale").innerText = tempScale + "x";

let settingsRectangle = document.getElementById("settings-rectangle");
let applySettingsButton = document.getElementById("apply-settings-button");
settingsRectangle.addEventListener("click", function () {
    if (tempScale === 1) {
        tempScale = 2;
    } else if (tempScale === 2) {
        tempScale = 4;
    } else if (tempScale === 4) {
        tempScale = 8;
    } else if (tempScale === 8) {
        tempScale = 12;
    } else if (tempScale === 12) {
        tempScale = 16;
        settingsRectangle.style.cursor = "zoom-out";
    } else if (tempScale === 16) {
        tempScale = 1;
        settingsRectangle.style.cursor = "zoom-in";
    }
    document.getElementById("label-scale").innerText = tempScale + "x";
    applySettingsButton.disabled = false;
});

document.addEventListener("DOMContentLoaded", function () {
    settingsRectangle.style.height = canvas.height * (settingsRectangle.offsetWidth / canvas.width) + "px";
});

window.addEventListener("resize", function () {
    settingsRectangle.style.height = canvas.offsetHeight * (settingsRectangle.offsetWidth / canvas.offsetWidth) + "px";
    document.getElementById("label-width").innerText = canvas.offsetWidth;
    document.getElementById("label-height").innerText = canvas.offsetHeight;
    applySettingsButton.disabled = false;
});

applySettingsButton.addEventListener("click", function () {
    SCALE = tempScale;
    mathFloorScaleTwo = Math.floor(SCALE / 2);
    mathCeilScaleTwo = Math.ceil(SCALE / 2);
    mathFloorScaleFour = Math.floor(SCALE / 4);
    mathCeilScaleFour = Math.ceil(SCALE / 4);
    maxOneAndMathFloorScaleTwo = Math.max(mathFloorScaleTwo, 1);
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    applySettingsButton.disabled = true;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ants = {};
    nests = [];
    objects = [];
    websocket.send(JSON.stringify({
        type: "SIMULATION_SET_BOUNDARIES",
        width: Math.floor(canvas.width / SCALE),
        height: Math.floor(canvas.height / SCALE)
    }));
    websocket.send(JSON.stringify({
        type: "SIMULATION_SET_SEED",
        seed: seed
    }));
    websocket.send(JSON.stringify({
        type: "SIMULATION_START"
    }));
});


let host = window.location.hostname;
let seed = new URLSearchParams(window.location.search).get("seed") || "0";

document.getElementById("uni-title-text").innerText = "Universe " + seed;

const websocket = new WebSocket(`ws://${host}:8765`);
const ctx = canvas.getContext("2d");


let ants = {};
let nests = [];
let objects = [];

let objectTypeColors = {
    "FOOD": "green",
    "WATER": "blue",
    "ROCK": "gray"
};

let tps_goal = 0;


websocket.onopen = function (event) {
    console.log("Connection established");
    websocket.send(JSON.stringify({
        type: "SIMULATION_SET_BOUNDARIES",
        width: Math.floor(canvas.width / SCALE),
        height: Math.floor(canvas.height / SCALE)
    }));
    websocket.send(JSON.stringify({
        type: "SIMULATION_SET_SEED",
        seed: seed
    }));
    websocket.send(JSON.stringify({
        type: "SIMULATION_START"
    }));
};

websocket.onerror = function (event) {
    document.getElementById("state").innerText = "Connection failed";
};



websocket.onmessage = function (event) {
    console.log(event.data);
    const data = JSON.parse(event.data);
    switch (data.type) {
        case "ANT_SPAWN":
            ants[data.ant.id] = data.ant;
            ctx.translate(data.ant.position.x * SCALE + mathFloorScaleTwo, data.ant.position.y * SCALE + mathFloorScaleTwo);
            if (SCALE >= 2) {
                ctx.rotate(data.ant.position.direction * Math.PI / 180);
            }
            ctx.fillStyle = data.ant.role !== "QUEEN" ? data.ant.color : "gold";
            ctx.fillRect(-mathCeilScaleFour, -mathCeilScaleTwo, maxOneAndMathFloorScaleTwo, SCALE);
            ctx.resetTransform();
            document.getElementById("ants").innerText = Object.keys(ants).length.toString();
            break;
        case "ANT_MOVE":
            if (ants[data.ant.id]) {
                ctx.save();
                ctx.translate(ants[data.ant.id].position.x * SCALE + mathFloorScaleTwo, ants[data.ant.id].position.y * SCALE + mathFloorScaleTwo);
                if (SCALE >= 2) {
                    ctx.rotate(ants[data.ant.id].position.direction * Math.PI / 180);
                }
                if (checkIfEntityIsInNest(ants[data.ant.id])) {
                    ctx.fillStyle = "lightgray";
                    ctx.fillRect(
                        -mathCeilScaleFour, -mathCeilScaleTwo, maxOneAndMathFloorScaleTwo, SCALE
                    );
                } else {
                    ctx.clearRect(
                        -mathCeilScaleFour, -mathCeilScaleTwo, maxOneAndMathFloorScaleTwo, SCALE
                    );
                }
                ctx.restore();
            } else {
                document.getElementById("ants").innerText = (Object.keys(ants).length + 1).toString();
            }
            ants[data.ant.id] = data.ant;
            ctx.translate(data.ant.position.x * SCALE + mathFloorScaleTwo, data.ant.position.y * SCALE + mathFloorScaleTwo);
            if (SCALE >= 2) {
                ctx.rotate(data.ant.position.direction * Math.PI / 180);
            }
            ctx.fillStyle = data.ant.role !== "QUEEN" ? data.ant.color : "gold";
            ctx.fillRect(-mathCeilScaleFour, -mathCeilScaleTwo, maxOneAndMathFloorScaleTwo, SCALE);
            ctx.resetTransform();
            break;
        case "ANT_DEATH":
            if (!ants[data.ant.id]) {
                break;
            }
            ctx.translate(ants[data.ant.id].position.x * SCALE + maxOneAndMathFloorScaleTwo, ants[data.ant.id].position.y * SCALE + mathFloorScaleTwo);
            if (SCALE >= 2) {
                ctx.rotate(ants[data.ant.id].position.direction * Math.PI / 180);
            }
            if (checkIfEntityIsInNest(ants[data.ant.id])) {
                ctx.clearRect(
                    -mathFloorScaleFour, -mathFloorScaleTwo, maxOneAndMathFloorScaleTwo, SCALE
                );
                ctx.fillStyle = "lightgray";
                ctx.fillRect(
                    -mathFloorScaleFour, -mathFloorScaleTwo, maxOneAndMathFloorScaleTwo, SCALE
                );
            } else {
                ctx.clearRect(
                    -mathFloorScaleFour, -mathFloorScaleTwo, maxOneAndMathFloorScaleTwo, SCALE
                );
            }
            ctx.resetTransform();
            delete ants[data.ant.id];
            document.getElementById("ants").innerText = Object.keys(ants).length.toString();
            break;
        case "SIMULATION_TPS":
            document.getElementById("tps").innerText = data.state;
            if (data.state < tps_goal) {
                document.getElementById("tps-history").innerText += data.state + ", ";
            }
            break;
        case "SIMULATION_SET_TPS":
            tps_goal = data.state;
            break;
        case "SIMULATION_START":
            document.getElementById("state").innerText = "Running";
            break;
        case "SIMULATION_END":
            document.getElementById("state").innerText = "Finished";
            document.getElementById("blur-overlay").style.opacity = 0;
            break;
        case "SIMULATION_PAUSE":
            document.getElementById("state").innerText = "Paused";
            document.getElementById("blur-overlay").style.opacity = 0;
            break;
        case "SIMULATION_RESUME":
            document.getElementById("state").innerText = "Running";
            break;
        case "SIMULATION_NOT_RUNNING":
            document.getElementById("state").innerText = "Not running";
            document.getElementById("blur-overlay").style.opacity = 0;
            break;
        case "NEST_SPAWN":
            nests.push(data.target);
            ctx.fillStyle = "lightgray"
            ctx.fillRect(data.target.area.position_1.x * SCALE, data.target.area.position_1.y * SCALE, data.target.area.width * SCALE, data.target.area.height * SCALE);
            break;
        case "OBJECT_SPAWN":
            objects.push(data.target);
            ctx.fillStyle = objectTypeColors[data.target.type];
            ctx.fillRect(data.target.position.x * SCALE, data.target.position.y * SCALE, Math.max(Math.floor(SCALE / 2), 1), Math.max(Math.floor(SCALE / 2), 1));
            break;
        case "OBJECT_DESPAWN":
            for (let i = 0; i < objects.length; i++) {
                if (objects[i].id === data.target.id) {
                    objects.splice(i, 1);
                    break;
                }
            }
            if (checkIfEntityIsInNest(data.target)) {
                ctx.clearRect(
                    data.target.position.x * SCALE, data.target.position.y * SCALE, Math.max(Math.floor(SCALE / 2), 1), Math.max(Math.floor(SCALE / 2), 1)
                );
                ctx.fillStyle = "lightgray";
                ctx.fillRect(
                    data.target.position.x * SCALE, data.target.position.y * SCALE, Math.max(Math.floor(SCALE / 2), 1), Math.max(Math.floor(SCALE / 2), 1)
                );
            } else {
                ctx.clearRect(
                    data.target.position.x * SCALE, data.target.position.y * SCALE, Math.max(Math.floor(SCALE / 2), 1), Math.max(Math.floor(SCALE / 2), 1)
                );
            }
            break;
        default:
            // Default case...
            break;
    }
};



function checkIfEntityIsInNest(entity) {
    for (let i = 0; i < nests.length; i++) {
        if (entity.position.x >= nests[i].area.position_1.x && entity.position.x <= nests[i].area.position_2.x && entity.position.y >= nests[i].area.position_1.y && entity.position.y <= nests[i].area.position_2.y) {
            return true;
        }
    }
    return false;
}

document.getElementById("start-button").addEventListener("click", function () {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ants = {};
    nests = [];
    objects = [];
    websocket.send(JSON.stringify({
        type: "SIMULATION_SET_BOUNDARIES",
        width: Math.floor(canvas.width / SCALE),
        height: Math.floor(canvas.height / SCALE)
    }));
    websocket.send(JSON.stringify({
        type: "SIMULATION_SET_SEED",
        seed: seed
    }));
    websocket.send(JSON.stringify({
        type: "SIMULATION_START"
    }));
});

document.getElementById("stop-button").addEventListener("click", function () {
    websocket.send(JSON.stringify({
        type: "SIMULATION_END"
    }));
    document.getElementById("blur-overlay").style.opacity = 1;
});

document.getElementById("pause-button").addEventListener("click", function () {
    websocket.send(JSON.stringify({
        type: "SIMULATION_PAUSE"
    }));
    document.getElementById("blur-overlay").style.opacity = 1;
});

document.getElementById("resume-button").addEventListener("click", function () {
    websocket.send(JSON.stringify({
        type: "SIMULATION_RESUME"
    }));
});
