<script>
  import { clamp } from "$lib/utils";

  export let min = 0;
  export let max = 100;
  export let width = "100%";

  export let start = min;
  export let end = max;

  // @ts-ignore
  let slider;

  // @ts-ignore
  function draggable(node) {
    // @ts-ignore
    let x;
    // @ts-ignore
    let y;

    // @ts-ignore
    function handleMousedown(event) {
      if (event.type === "touchstart") {
        event = event.touches[0];
      }
      x = event.clientX;
      y = event.clientY;
      node.dispatchEvent(new CustomEvent("dragstart", { detail: { x, y } }));
      window.addEventListener("mousemove", handleMousemove);
      window.addEventListener("mouseup", handleMouseup);
      window.addEventListener("touchmove", handleMousemove);
      window.addEventListener("touchend", handleMouseup);
    }

    // @ts-ignore
    function handleMousemove(event) {
      if (event.type === "touchmove") {
        event = event.changedTouches[0];
      }

      // @ts-ignore
      const dx = event.clientX - x;

      // @ts-ignore
      const dy = event.clientY - y;
      x = event.clientX;
      y = event.clientY;
      node.dispatchEvent(
        new CustomEvent("dragmove", { detail: { x, y, dx, dy } })
      );
    }

    // @ts-ignore
    function handleMouseup(event) {
      x = event.clientX;
      y = event.clientY;
      node.dispatchEvent(new CustomEvent("dragend", { detail: { x, y } }));
      window.removeEventListener("mousemove", handleMousemove);
      window.removeEventListener("mouseup", handleMouseup);
      window.removeEventListener("touchmove", handleMousemove);
      window.removeEventListener("touchend", handleMouseup);
    }
    node.addEventListener("mousedown", handleMousedown);
    node.addEventListener("touchstart", handleMousedown);
    return {
      destroy() {
        node.removeEventListener("mousedown", handleMousedown);
        node.removeEventListener("touchstart", handleMousedown);
      },
    };
  }

  // @ts-ignore
  function percentToValue(p) {
    return clamp(Math.round(min + p * (max - min)), min, max);
  }

  // @ts-ignore
  function valueToPercent(val) {
    return (clamp(val, min, max) - min) / (max - min);
  }

  // @ts-ignore
  function setHandlePosition(which) {
    // @ts-ignore
    return function (evt) {
      // @ts-ignore
      const { left, right } = slider.getBoundingClientRect();
      const parentWidth = right - left;
      const p = Math.min(Math.max((evt.detail.x - left) / parentWidth, 0), 1);
      const v = percentToValue(p);
      if (which === "start") {
        start = clamp(v, min, end);
      } else {
        end = clamp(v, start, max);
      }
    };
  }
</script>

<div class="double-range-wrapper" style="width: {width};">
  <div class="slider" bind:this={slider}>
    <div
      class="body"
      style="left: {100 * valueToPercent(start)}%; right: {100 *
        (1 - valueToPercent(end))}%;"
    ></div>
    <div
      class="handle"
      data-which="start"
      use:draggable
      on:dragmove|preventDefault|stopPropagation={setHandlePosition("start")}
      style="left: {100 * valueToPercent(start)}%"
    ></div>
    <div
      class="handle"
      data-which="end"
      use:draggable
      on:dragmove|preventDefault|stopPropagation={setHandlePosition("end")}
      style="left: {100 * valueToPercent(end)}%"
    ></div>
  </div>
  <div class="labels">
    <span>{start}</span>
    <span>{end}</span>
  </div>
</div>

<style>
  .double-range-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }
  .slider {
    position: relative;
    width: 100%;
    height: 6px;
    background-color: #e2e2e2;
    box-shadow:
      inset 0 7px 10px -5px #4a4a4a,
      inset 0 -1px 0px 0px #9c9c9c;
    border-radius: 1px;
  }
  .handle {
    position: absolute;
    top: 50%;
    width: 0;
    height: 0;
  }
  .handle:after {
    content: " ";
    box-sizing: border-box;
    position: absolute;
    border-radius: 50%;
    width: 16px;
    height: 16px;
    background-color: #fdfdfd;
    border: 1px solid #7b7b7b;
    transform: translate(-50%, -50%);
  }
  .handle:active:after {
    background-color: #ddd;
    z-index: 9;
  }
  .body {
    position: absolute;
    top: 0;
    bottom: 0;
    background-color: #34a1ff;
  }
  .labels {
    display: flex;
    justify-content: space-between;
    width: 100%;
    font-size: 14px;
    color: #333;
  }
</style>
