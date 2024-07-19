(function() {
  let startX, startY, endX, endY;
  let isDrawing = false;
  let selectionBox;

  function initializeSelectionBox() {
    selectionBox = document.createElement('div');
    selectionBox.style.position = 'absolute';
    selectionBox.style.border = '2px dashed #000';
    selectionBox.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
    selectionBox.style.display = 'none';
    document.body.appendChild(selectionBox);
  }

  function onMouseDown(event) {
    isDrawing = true;
    startX = event.pageX;
    startY = event.pageY;
    selectionBox.style.left = `${startX}px`;
    selectionBox.style.top = `${startY}px`;
    selectionBox.style.width = '0px';
    selectionBox.style.height = '0px';
    selectionBox.style.display = 'block';
  }

  function onMouseMove(event) {
    if (!isDrawing) return;
    endX = event.pageX;
    endY = event.pageY;
    selectionBox.style.width = `${Math.abs(endX - startX)}px`;
    selectionBox.style.height = `${Math.abs(endY - startY)}px`;
    selectionBox.style.left = `${Math.min(startX, endX)}px`;
    selectionBox.style.top = `${Math.min(startY, endY)}px`;
  }

  function onMouseUp(event) {
    isDrawing = false;
    selectionBox.style.display = 'none';
    selectProfilesWithinRectangle();
  }

  function selectProfilesWithinRectangle() {
    const profiles = [];
    const rect = selectionBox.getBoundingClientRect();
    document.querySelectorAll('.search-result__info a').forEach(a => {
      const linkRect = a.getBoundingClientRect();
      if (linkRect.top >= rect.top && linkRect.bottom <= rect.bottom && linkRect.left >= rect.left && linkRect.right <= rect.right) {
        profiles.push({
          name: a.innerText,
          url: a.href
        });
      }
    });

    chrome.runtime.sendMessage({ action: 'profiles', profiles: profiles });
  }

  initializeSelectionBox();
  document.addEventListener('mousedown', onMouseDown);
  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', onMouseUp);
})();
