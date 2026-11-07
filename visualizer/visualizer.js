let rootNode = null;
let svg = null;
let g = null;
let treeLayout = null;
let zoomBehavior = null;
let tooltip = null;
let nodeCounter = 0;

const COLORS = {
  root: '#2563eb',
  function: '#7c3aed',
  control: '#dc2626',
  operator: '#ea580c',
  literal: '#16a34a',
  identifier: '#0284c7',
  declaration: '#0d9488',
  statement: '#4f46e5',
  structure: '#64748b'
};

function initVisualizer(data) {
  const container = document.getElementById('tree-container');
  if (!container) return;

  d3.select('#tree-container').selectAll('*').remove();

  tooltip = d3.select('body').selectAll('.d3-tooltip').data([0]).join('div')
    .attr('class', 'd3-tooltip')
    .style('opacity', 0);

  svg = d3.select('#tree-container')
    .append('svg')
    .attr('width', '100%')
    .attr('height', '100%');

  g = svg.append('g').attr('class', 'tree-viewport');

  zoomBehavior = d3.zoom()
    .scaleExtent([0.15, 2.5])
    .on('zoom', (event) => {
      g.attr('transform', event.transform);
    });

  svg.call(zoomBehavior);

  treeLayout = d3.tree().nodeSize([140, 70]);

  rootNode = d3.hierarchy(data, d => d.children);
  rootNode.x0 = (container.clientWidth || 600) / 2;
  rootNode.y0 = 40;

  // Початкове згортання глибше 3 рівнів для наочності
  function collapseAfterDepth(d) {
    if (d.children) {
      if (d.depth >= 3) {
        d._children = d.children;
        d.children = null;
      }
      if (d._children) d._children.forEach(collapseAfterDepth);
      if (d.children) d.children.forEach(collapseAfterDepth);
    }
  }
  collapseAfterDepth(rootNode);

  update(rootNode);

  setTimeout(fitToScreen, 150);
}

function update(source) {
  const treeData = treeLayout(rootNode);
  const nodes = treeData.descendants();
  const links = treeData.links();

  nodes.forEach(d => {
    d.y = d.depth * 75 + 40;
  });

  const node = g.selectAll('g.node')
    .data(nodes, d => d.id || (d.id = ++nodeCounter));

  const nodeEnter = node.enter().append('g')
    .attr('class', d => 'node' + (d._children ? ' node-collapsed' : ''))
    .attr('transform', d => `translate(${source.x0 || source.x},${source.y0 || source.y})`)
    .on('click', (event, d) => {
      if (d.children) {
        d._children = d.children;
        d.children = null;
      } else if (d._children) {
        d.children = d._children;
        d._children = null;
      }
      update(d);
    })
    .on('mouseover', (event, d) => {
      tooltip.style('opacity', 1);
      const valText = d.data.val !== undefined ? `<br>Значення: <b>${d.data.val}</b>` : '';
      const typeText = d.data.dataType ? `<br>Тип: <b>${d.data.dataType}</b>` : '';
      tooltip.html(`<b>${d.data.type || 'Node'}</b><br>${d.data.name}${valText}${typeText}`)
        .style('left', (event.pageX + 12) + 'px')
        .style('top', (event.pageY - 20) + 'px');
    })
    .on('mouseout', () => {
      tooltip.style('opacity', 0);
    });

  nodeEnter.append('circle')
    .attr('r', 6)
    .style('fill', d => d._children ? '#f59e0b' : '#ffffff')
    .style('stroke', d => COLORS[d.data.category] || '#2563eb');

  nodeEnter.append('text')
    .attr('dy', d => d.children || d._children ? -10 : 16)
    .attr('text-anchor', 'middle')
    .text(d => {
      const name = d.data.name || '';
      return name.length > 20 ? name.substring(0, 18) + '..' : name;
    });

  const nodeUpdate = node.merge(nodeEnter).transition().duration(250)
    .attr('class', d => 'node' + (d._children ? ' node-collapsed' : ''))
    .attr('transform', d => `translate(${d.x},${d.y})`);

  nodeUpdate.select('circle')
    .attr('r', 6)
    .style('fill', d => d._children ? '#f59e0b' : '#ffffff')
    .style('stroke', d => COLORS[d.data.category] || '#2563eb');

  node.exit().transition().duration(200)
    .attr('transform', d => `translate(${source.x},${source.y})`)
    .remove();

  const link = g.selectAll('path.link')
    .data(links, d => d.target.id);

  const linkEnter = link.enter().insert('path', 'g')
    .attr('class', 'link')
    .attr('d', () => {
      const o = { x: source.x0 || source.x, y: source.y0 || source.y };
      return diagonal(o, o);
    });

  link.merge(linkEnter).transition().duration(250)
    .attr('d', d => diagonal(d.source, d.target));

  link.exit().transition().duration(200)
    .attr('d', () => {
      const o = { x: source.x, y: source.y };
      return diagonal(o, o);
    })
    .remove();

  nodes.forEach(d => {
    d.x0 = d.x;
    d.y0 = d.y;
  });
}

function diagonal(s, d) {
  return `M ${s.x} ${s.y}
          C ${s.x} ${(s.y + d.y) / 2},
            ${d.x} ${(s.y + d.y) / 2},
            ${d.x} ${d.y}`;
}

function fitToScreen() {
  if (!g || !svg) return;
  const container = document.getElementById('tree-container');
  if (!container) return;

  const width = container.clientWidth || 600;
  const height = container.clientHeight || 500;
  const bbox = g.node().getBBox();

  if (!bbox || bbox.width === 0 || bbox.height === 0) return;

  const pad = 30;
  const scale = Math.min((width - pad * 2) / bbox.width, (height - pad * 2) / bbox.height, 1.2);
  const midX = bbox.x + bbox.width / 2;
  const midY = bbox.y + bbox.height / 2;

  const tx = width / 2 - scale * midX;
  const ty = height / 2 - scale * midY;

  svg.transition().duration(300).call(
    zoomBehavior.transform,
    d3.zoomIdentity.translate(tx, ty).scale(scale)
  );
}

function expandAll() {
  if (!rootNode) return;
  function exp(d) {
    if (d._children) {
      d.children = d._children;
      d._children = null;
    }
    if (d.children) d.children.forEach(exp);
  }
  exp(rootNode);
  update(rootNode);
  setTimeout(fitToScreen, 280);
}

function collapseAll() {
  if (!rootNode) return;
  function col(d) {
    if (d.children) {
      d._children = d.children;
      d.children = null;
      d._children.forEach(col);
    }
  }
  if (rootNode.children) rootNode.children.forEach(col);
  update(rootNode);
  setTimeout(fitToScreen, 280);
}
