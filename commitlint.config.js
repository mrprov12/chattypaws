// Workspace scopes: repo (root), backend-python, pwa.
// When adding a new subrepo, add its scope here and to .cursor/rules/conventional-commits-workspace.mdc
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'scope-enum': [2, 'always', ['repo', 'backend-python', 'pwa']],
  },
};
