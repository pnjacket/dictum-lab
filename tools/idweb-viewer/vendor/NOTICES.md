# Third-party notices — vendored libraries

The ID-web viewer vendors three JavaScript libraries so it runs fully offline
(no CDN, no build step). All three are under the **MIT License** — the same
license as dictum-lab — and each copyright + permission notice is retained in
full in the `LICENSE.*` file named below, satisfying the MIT license's
conditions for redistribution.

| File | Project | Version | Copyright | License text |
|---|---|---|---|---|
| `cytoscape.min.js` | [Cytoscape.js](https://js.cytoscape.org/) | 3.33.1 | © 2016–2025, The Cytoscape Consortium | [`LICENSE.cytoscape`](LICENSE.cytoscape) (MIT) |
| `dagre.min.js` | [dagre](https://github.com/dagrejs/dagre) | 0.8.5 | © 2012–2014 Chris Pettitt | [`LICENSE.dagre`](LICENSE.dagre) (MIT) |
| `cytoscape-dagre.js` | [cytoscape-dagre](https://github.com/cytoscape/cytoscape.js-dagre) | 2.5.0 | © 2016–2018, 2020, 2022, The Cytoscape Consortium | [`LICENSE.cytoscape-dagre`](LICENSE.cytoscape-dagre) (MIT) |

Files are vendored unmodified from the npm registry (`unpkg.com/<pkg>@<version>`).
When upgrading a library: replace the file, update this table's version, and
re-copy its LICENSE if the copyright line changed.
