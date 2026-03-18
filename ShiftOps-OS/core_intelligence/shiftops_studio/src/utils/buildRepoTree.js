// utils/buildRepoTree.js

export function buildRepoTree(repo) {
  const root = {};

  Object.keys(repo).forEach((path) => {
    const parts = path.split("/");
    let current = root;

    parts.forEach((part, index) => {
      const isFile = index === parts.length - 1;

      if (!current[part]) {
        current[part] = isFile
          ? { type: "file", content: repo[path], path: path }
          : { type: "folder", children: {} };
      }

      if (!isFile) {
        current = current[part].children;
      }
    });
  });

  return root;
}
