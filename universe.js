// Utility Functions
function fitCanvasToContainer(canvas) {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
}

function updateLabel(id, text) {
    document.getElementById(id).innerText = text;
}

function updateCanvasSize(canvas) {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
}

function calculateScales(scale) {
    return {
        floorHalf: Math.floor(scale / 2),
        ceilHalf: Math.ceil(scale / 2),
        floorQuarter: Math.floor(scale / 4),
        ceilQuarter: Math.ceil(scale / 4),
        maxFloorHalf: Math.max(Math.floor(scale / 2), 1),
        ceilNegHalf: Math.ceil(-scale / 2),
        ceilNegQuarter: Math.ceil(-scale / 4),
    };
}

// Initial Setup
const canvas = document.getElementById("canvas");
const nestCanvas = document.getElementById("nest-canvas");

fitCanvasToContainer(canvas);
fitCanvasToContainer(nestCanvas);

let SCALE = 4;
let scales = calculateScales(SCALE);

let tempScale = SCALE;
updateLabel("label-width", canvas.width);
updateLabel("label-height", canvas.height);
updateLabel("label-scale", tempScale + "x");

const settingsRectangle = document.getElementById("settings-rectangle");
const applySettingsButton = document.getElementById("apply-settings-button");

settingsRectangle.addEventListener("click", handleSettingsClick);
document.addEventListener("DOMContentLoaded", adjustSettingsRectangleHeight);
window.addEventListener("resize", handleResize);

applySettingsButton.addEventListener("click", applySettings);

let host = window.location.hostname;
let seed = new URLSearchParams(window.location.search).get("seed") || "0";
// let ignoreMessages = false;

updateLabel("uni-title-text", seed);

// WebSocket Setup and Error Handling
let websocket;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function setupWebSocket() {
    websocket = new WebSocket(`ws://${host}:8765`);

    websocket.onopen = handleWebSocketOpen;
    websocket.onerror = handleWebSocketError;
    websocket.onmessage = handleWebSocketMessage;
    websocket.onclose = handleWebSocketClose;
}

setupWebSocket();

const ctx = canvas.getContext("2d");
const nestCtx = nestCanvas.getContext("2d");

let ants = {};
let nests = [];
let objects = [];

const objectTypeColors = {
    "FOOD": "green",
    "WATER": "blue",
    "ROCK": "gray"
};

let tps_goal = 0;

websocket.onopen = handleWebSocketOpen;
websocket.onerror = handleWebSocketError;
websocket.onmessage = handleWebSocketMessage;

const antCountElement = document.getElementById("ants");
const tpsElement = document.getElementById("tps");
const tpsHistoryElement = document.getElementById("tps-history");
const stateElement = document.getElementById("state");
const blurOverlayElement = document.getElementById("blur-overlay");
const roundElement = document.getElementById("round");

document.getElementById("start-button").addEventListener("click", startSimulation);
document.getElementById("stop-button").addEventListener("click", stopSimulation);
document.getElementById("pause-button").addEventListener("click", pauseSimulation);
document.getElementById("resume-button").addEventListener("click", resumeSimulation);

document.getElementById("tps-input").addEventListener("input", handleTpsInput);
document.getElementById("rounds-input").addEventListener("input", handleRoundsInput);

let messageQueue = [];
let processingMessages = false;

// Event Handlers
function handleSettingsClick() {
    if (settingsRectangle.disabled) return;
    tempScale = (tempScale === 16) ? 1 : tempScale * 2;
    settingsRectangle.style.cursor = (tempScale === 16) ? "zoom-out" : "zoom-in";
    updateLabel("label-scale", tempScale + "x");
    applySettingsButton.disabled = false;
}

function adjustSettingsRectangleHeight() {
    settingsRectangle.style.height = `${canvas.height * (settingsRectangle.offsetWidth / canvas.width)}px`;
}

function handleResize() {
    adjustSettingsRectangleHeight();
    updateLabel("label-width", canvas.offsetWidth);
    updateLabel("label-height", canvas.offsetHeight);
    applySettingsButton.disabled = false;
}

function applySettings() {
    // ignoreMessages = true;
    document.getElementById("overload-notification").style.display = "unset";
    blurOverlayElement.style.opacity = 1;
    SCALE = tempScale;
    scales = calculateScales(SCALE);
    updateCanvasSize(canvas);
    updateCanvasSize(nestCanvas);
    applySettingsButton.disabled = true;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    nestCtx.clearRect(0, 0, nestCanvas.width, nestCanvas.height);
    ants = {};
    nests = [];
    objects = [];
    sendWebSocketMessage({
        type: "SIMULATION_SET_BOUNDARIES",
        width: Math.floor(canvas.width / SCALE),
        height: Math.floor(canvas.height / SCALE)
    });
    sendWebSocketMessage({
        type: "SIMULATION_SET_SEED", seed: seed
    });
    sendWebSocketMessage({
        type: "SIMULATION_START"
    });
}

function handleWebSocketOpen() {
    console.log("Connection established");
    sendWebSocketMessage({
        type: "SIMULATION_SET_BOUNDARIES",
        width: Math.floor(canvas.width / SCALE),
        height: Math.floor(canvas.height / SCALE)
    });
    sendWebSocketMessage({
        type: "SIMULATION_SET_SEED", seed: seed
    });
    sendWebSocketMessage({
        type: "SIMULATION_START"
    });
}

function handleWebSocketError() {
    updateLabel("state", "Connection error");
    attemptReconnect();
}

function handleWebSocketClose() {
    updateLabel("state", "Connection closed");
    attemptReconnect();
}

function attemptReconnect() {
    if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        setTimeout(setupWebSocket, 2000); // Try to reconnect after 2 seconds
    } else {
        displayWebSocketUnavailable();
    }
}

function displayWebSocketUnavailable() {
    updateLabel("state", "WebSocket not available");
    document.getElementById("overload-notification").style.display = "none";
    document.getElementById("websocket-error-notification").style.display = "block";
    disableAllControls();
}

function disableAllControls() {
    document.querySelectorAll("button, input").forEach(element => {
        if (!("doNotDisable" in element.dataset)) {
            element.disabled = true;
        }
    });
    blurOverlayElement.style.opacity = 1;
    settingsRectangle.disabled = true;
    settingsRectangle.style.cursor = "not-allowed";
}
function handleWebSocketMessage(event) {
    messageQueue.push(event.data);
    if (!processingMessages) {
        processMessageQueue();
    }
}

function processMessageQueue() {
    processingMessages = true;
    requestAnimationFrame(() => {
        while (messageQueue.length > 0) {
            const event = messageQueue.shift();
            handleEvent(JSON.parse(event));
        }
        processingMessages = false;
    });
}

const handlers = {
    "ANT_SPAWN": handleAntSpawn,
    "ANT_MOVE": handleAntMove,
    "ANT_DEATH": handleAntDeath,
    "SIMULATION_TPS": updateTps,
    "SIMULATION_SET_TPS": setTpsGoal,
    "SIMULATION_START": startSimulationHandler,
    "SIMULATION_END": endSimulationHandler,
    "SIMULATION_PAUSE": pauseSimulationHandler,
    "SIMULATION_RESUME": resumeSimulationHandler,
    "ERROR_SIMULATION_NOT_RUNNING": errorSimulationNotRunning,
    "NEST_SPAWN": handleNestSpawn,
    "OBJECT_SPAWN": handleObjectSpawn,
    "OBJECT_DESPAWN": handleObjectDespawn,
    "SIMULATION_CURRENT_ROUND": updateCurrentRound
};

function handleEvent(data) {
    // if (ignoreMessages && data.type !== "SIMULATION_START") {
    //     return;
    // }

    const handler = handlers[data.type];
    if (handler) {
        handler(data);
    }
}

function handleAntSpawn({ ant }) {
    ants[ant.id] = ant;
    drawAnt(ant);
    updateAntCount();
}

function handleAntMove({ ant }) {
    if (ants[ant.id]) {
        clearAnt(ants[ant.id]);
    } else {
        updateAntCount(1);
    }
    ants[ant.id] = ant;
    drawAnt(ant);
}

function handleAntDeath({ ant }) {
    if (!ants[ant.id]) return;
    clearAnt(ants[ant.id]);
    delete ants[ant.id];
    updateAntCount();
}

function drawAnt(ant) {
    ctx.save();
    ctx.translate(ant.position.x * SCALE + scales.floorHalf, ant.position.y * SCALE + scales.floorHalf);
    if (SCALE >= 2) {
        ctx.rotate(ant.position.direction * Math.PI / 180);
    }
    ctx.fillStyle = ant.role !== "QUEEN" ? ant.color : "gold";
    ctx.fillRect(scales.ceilNegQuarter, scales.ceilNegHalf, scales.maxFloorHalf, SCALE);
    ctx.restore();
}

function clearAnt(ant) {
    ctx.save();
    ctx.translate(ant.position.x * SCALE + scales.floorHalf, ant.position.y * SCALE + scales.floorHalf);
    if (SCALE >= 2) {
        ctx.rotate(ant.position.direction * Math.PI / 180);
    }
    ctx.clearRect(scales.ceilNegQuarter, scales.ceilNegHalf, scales.maxFloorHalf, SCALE);
    ctx.restore();
}

function updateAntCount(delta = 0) {
    const antCount = Object.keys(ants).length + delta;
    antCountElement.innerText = antCount.toString();
}

function updateTps({ state }) {
    tpsElement.innerText = state;
    if (state < tps_goal) {
        tpsHistoryElement.innerText += state + ", ";
    }
}

function setTpsGoal({ state }) {
    tps_goal = state;
}

function startSimulationHandler() {
    // ignoreMessages = false;
    stateElement.innerText = "Running";
    document.getElementById("websocket-error-notification").style.display = "none";
    document.getElementById("overload-notification").style.display = "none";
    blurOverlayElement.style.opacity = 0;
    nestCtx.clearRect(0, 0, nestCanvas.width, nestCanvas.height);
}

function endSimulationHandler() {
    stateElement.innerText = "Finished";
    document.getElementById("websocket-error-notification").style.display = "none";
    document.getElementById("overload-notification").style.display = "none";
    blurOverlayElement.style.opacity = 0;
}

function pauseSimulationHandler() {
    stateElement.innerText = "Paused";
    document.getElementById("websocket-error-notification").style.display = "none";
    document.getElementById("overload-notification").style.display = "none";
    blurOverlayElement.style.opacity = 0;
}

function resumeSimulationHandler() {
    stateElement.innerText = "Running";
}

function errorSimulationNotRunning() {
    stateElement.innerText = "Not running";
    document.getElementById("websocket-error-notification").style.display = "none";
    document.getElementById("overload-notification").style.display = "none";
    blurOverlayElement.style.opacity = 0;
}

function handleNestSpawn({ target }) {
    nests.push(target);
    nestCtx.fillStyle = "lightgray";
    nestCtx.fillRect(target.area.position_1.x * SCALE, target.area.position_1.y * SCALE, target.area.width * SCALE, target.area.height * SCALE);
}

function handleObjectSpawn({ target }) {
    objects.push(target);
    ctx.fillStyle = objectTypeColors[target.type];
    ctx.fillRect(target.position.x * SCALE, target.position.y * SCALE, scales.maxFloorHalf, scales.maxFloorHalf);
}

function handleObjectDespawn({ target }) {
    objects = objects.filter(obj => obj.id !== target.id);
    clearObject(target);
}

function clearObject(target) {
    ctx.clearRect(target.position.x * SCALE, target.position.y * SCALE, scales.maxFloorHalf, scales.maxFloorHalf);
}

function updateCurrentRound({ state }) {
    roundElement.innerText = state.toString();
}

// Simulation Control
function startSimulation() {
    // ignoreMessages = true;
    document.getElementById("overload-notification").style.display = "unset";
    blurOverlayElement.style.opacity = 1;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    nestCtx.clearRect(0, 0, nestCanvas.width, nestCanvas.height);
    ants = {};
    nests = [];
    objects = [];
    if (tps_goal > 0) {
        sendWebSocketMessage({
            type: "SIMULATION_SET_TPS",
            tps: tps_goal
        });
    }
    const rounds = parseInt(document.getElementById("rounds-input").value);
    if (rounds > 0) {
        sendWebSocketMessage({
            type: "SIMULATION_SET_ROUNDS",
            rounds: rounds
        });
    }
    sendWebSocketMessage({
        type: "SIMULATION_SET_BOUNDARIES",
        width: Math.floor(canvas.width / SCALE),
        height: Math.floor(canvas.height / SCALE)
    });
    sendWebSocketMessage({
        type: "SIMULATION_SET_SEED", seed: seed
    });
    sendWebSocketMessage({
        type: "SIMULATION_START"
    });
}

function stopSimulation() {
    sendWebSocketMessage({ type: "SIMULATION_END" });
    document.getElementById("overload-notification").style.display = "unset";
    blurOverlayElement.style.opacity = 1;
}

function pauseSimulation() {
    sendWebSocketMessage({ type: "SIMULATION_PAUSE" });
    document.getElementById("overload-notification").style.display = "unset";
    blurOverlayElement.style.opacity = 1;
}

function resumeSimulation() {
    sendWebSocketMessage({ type: "SIMULATION_RESUME" });
}

function handleTpsInput() {
    tps_goal = parseInt(document.getElementById("tps-input").value);
    if (isNaN(tps_goal) || tps_goal < 0) {
        tps_goal = 0;
    } else if (tps_goal > 1000) {
        tps_goal = 1000;
    }
    document.getElementById("tps-input").value = tps_goal;
    updateLabel("tps", tps_goal);
    sendWebSocketMessage({
        type: "SIMULATION_SET_TPS",
        tps: tps_goal
    });
}

function handleRoundsInput() {
    let rounds = parseInt(document.getElementById("rounds-input").value);
    if (isNaN(rounds) || rounds < 0) {
        rounds = 0;
    }
    document.getElementById("rounds-input").value = rounds;
    sendWebSocketMessage({
        type: "SIMULATION_SET_ROUNDS",
        rounds: rounds
    });
}

function sendWebSocketMessage(message) {
    if (websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify(message));
    } else {
        handleWebSocketError();
    }
}