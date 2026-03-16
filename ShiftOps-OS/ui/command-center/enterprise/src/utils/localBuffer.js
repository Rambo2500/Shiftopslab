const KEY = "opsai_pending_assessments";

export function loadPending() {
  const raw = localStorage.getItem(KEY);
  return raw ? JSON.parse(raw) : [];
}

export function savePending(list) {
  localStorage.setItem(KEY, JSON.stringify(list));
}

export function addPending(item) {
  const list = loadPending();
  const localId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
  const buffered = { ...item, localId, timestamp: new Date().toISOString() };
  list.push(buffered);
  savePending(list);
  return localId;
}

export function removePending(localId) {
  const list = loadPending().filter(x => x.localId !== localId);
  savePending(list);
}

export function pendingCount() {
  return loadPending().length;
}
