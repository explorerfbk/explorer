/* global Contents, d3, he, Mustache,  s, _ */
;(function($) {
  
  function OrganizationChart(options) {
    
    var self = this;
    
    self.options = options;
    
    self.width = self.options.container.width();
    
    self.height = self.options.defaultHeight;
    
    self.counter = 0;
    
    self.root = null;
    
    self.treeMap = null;
    
    self.svg = d3.select(self.options.container[0])
      .append('svg')
      .attr('xmlns', 'http://www.w3.org/2000/svg')
      .attr('xlink', 'http://www.w3.org/1999/xlink')
      .attr('width', self.width)
      .attr('height', self.height);

    self.svg.on('mouseout', function() {
      self.svg.selectAll('g.node').each(function() {
        self.unhighlight(this);
      });
    });

    self.g = null;
    
    this.collapse = function(d) {
      if (d.children) {
        d._children = d.children;
        d._children.forEach(self.collapse);
        d.children = null;
      }
    };
    
    this.diagonal = function(s, d) {
      return 'M ' + (s.x + self.options.margin.horizontal) + ' ' + (s.y + self.options.margin.vertical) +
        'C ' + ((s.x + d.x + (self.options.margin.horizontal * 2)) / 2) + ' ' + (s.y + self.options.margin.vertical) +
        ', ' + ((s.x + d.x + (self.options.margin.horizontal * 2)) / 2) + ' ' + (d.y + self.options.margin.vertical) +
        ', ' + (d.x + self.options.margin.horizontal) + ' ' + (d.y + self.options.margin.vertical);
    };
    
    this.highlight = function(node) {
      d3.select(node).select('.overlay')
        .transition()
        .duration(self.options.duration)
        .attr('opacity', 1)
        .attr('transform', 'scale(1.00) translate(-120, -104)')
        .style('pointer-events', 'auto');
    };

    this.unhighlight = function(node) {
      d3.select(node).select('.overlay')
        .transition()
        .duration(self.options.duration)
        .attr('opacity', 0)
        .attr('transform', 'scale(0.33) translate(-120, -72)')
        .style('pointer-events', 'none');
    };
    
    this.wrap = function(text, width) {
      text.each(function(d) {
        var values = [],
          text = d3.select(this),
          words,
          word,
          line,
          lineNumber = 0,
          lineHeight = 1.1,
          y = parseInt(text.attr('y')),
          dy = parseFloat(text.attr('dy')),
          tspan;

        text.text(null);

        if (!!d.data.data.role) {
          values.push(d.data.data.role);
        }

        values.push(d.data.data.name);

        $.each(values, function(i, value) {
          words = value.split(/\s+/).reverse();
          line = [];
          tspan = text.append('tspan').attr('x', 0).attr('y', y).attr('dy', (lineNumber++ * lineHeight) + dy + 'em');

          while (!!(word = words.pop())) {
            line.push(word);
            tspan.text(he.decode(line.join(' ')));
            if (tspan.node().getComputedTextLength() > width) {
              line.pop();
              tspan.text(he.decode(line.join(' ')));
              line = [word];
              tspan = text.append('tspan').attr('x', 0).attr('y', y).attr('dy', (lineNumber++ * lineHeight) + dy + 'em').text(he.decode(word));
            }
          }
        });
      });
    };
    
    this.click = function(d) {
      self.root.descendants().forEach(function(n) {
        if (n.id !== d.id && n.depth === d.depth && n.children) {
          n.descendants().forEach(function(c) {
            if (c.children) {
              c._children = c.children;
              c.children = null;
            }
          });
        }
      });

      if (d.children) {
        d._children = d.children;
        d.children = null;
      } else {
        d.children = d._children;
        d._children = null;
      }

      self.update(d);

      var nestedCollapse;

      nestedCollapse = function(n) {
        $.each(n.children || n._children || [], function(i, c) {
          if (c.children) {
            c._children = c.children;
            c.children = null;
          }

          nestedCollapse(c);
        });
      };

      nestedCollapse(d);
    };
    
    this.update = function(source) {
      self.height = Math.max(self.options.defaultHeight, d3.max(self.treeMap(self.root).descendants(), function(d) { return d.depth; }) * self.options.levelHeight);
      
      self.width = self.options.container.width();

      self.svg.transition().duration(self.options.duration)
        .attr('width', self.width)
        .attr('height', self.height);

      self.treeMap = d3.tree().size([
        self.width - self.options.margin.horizontal * 2,
        self.height - self.options.margin.vertical * 2
      ]);

      var treeData = self.treeMap(self.root);

      var nodes = treeData.descendants();

      var nodeWidth = 0, dx = 0;

      nodes.forEach(function(d) {
        d.y = d.depth * 180;
        nodeWidth = Math.abs(Math.min(nodeWidth, d.x - dx));
        dx = d.x;
      });

      if (!nodeWidth) {
        nodeWidth = 180;
      }

      var node = self.g.selectAll('g.node')
        .data(nodes, function(d) { return d.id || (d.id = ++self.counter); });

      var nodeEnter = node.enter().append('g')
        .attr('class', 'node')
        .attr('transform', function(d) {
          return 'translate(' + (source.x0 + self.options.margin.horizontal) + ',' + (source.y0 + self.options.margin.vertical) + ')';
        });

      nodeEnter.append('text')
        .attr('class', 'label')
        .attr('dy', '.35em')
        .attr('x', 0)
        .attr('y', 0)
        .attr('text-anchor', 'middle')
        .text(function(d) { return he.decode(d.data.data.name); })
        .call(self.wrap, Math.round(nodeWidth))
        .each(function(d) {
          var bbox = this.getBBox();
          var offset = d.children || d._children ? (Math.round(bbox.height) + 24) * -1 : 38;
          d3.select(this).style('transform', 'translateY(' + offset + 'px)');
        });
      
      nodeEnter.each(function(d) {
        if (!!d.data.data.details) {
          d3.select(this).append('g')
            .attr('class', 'overlay')
            .attr('opacity', 0)
            .attr('transform', 'scale(0.33) translate(-120, -72)')
            .on('mouseover', function(d) {
              if (!!d.data.data.details) {
                self.highlight(this.parentNode);
              }
            })
            .on('mouseout', function(d) {
              self.unhighlight(this.parentNode);
            })
            .each(function(d) {
              d3.select(this).append('rect')
                .attr('width', 240)
                .attr('height', 96);

              d3.select(this).append('text')
                .attr('x', 8)
                .attr('y', 16)
                .attr('dy', '0.35em')
                .text(he.decode(d.data.data.name));
              
              if (!!d.data.data.details.salary && !!d.data.data.details.salary.value) {
                d3.select(this).append('text')
                  .attr('x', 8)
                  .attr('y', 20)
                  .attr('dy', '1.35em')
                  .text(he.decode((!!d.data.data.details.salary.label ? d.data.data.details.salary.label : 'Earnings') + ': ' + d.data.data.details.salary.value));
              }

              d3.select(this).append('a')
                .attr('xlink:href', d.data.data.permalink || d.data.data.details.permalink)
                .attr('target', '_blank')
                .append('text')
                .attr('x', 8)
                .attr('y', 24)
                .attr('dy', '2.35em')
                .text('maggiori informazioni');
            });
        }
      });
      
      nodeEnter.append('circle')
        .attr('class', function(d) { return !!d.children || !!d._children ? 'element has-children' : 'element'; })
        .attr('r', 1e-6)
        .attr('cursor', function(d) {
          if (!!d.children || !!d._children) {
            return 'pointer';
          } else {
            return 'default';
          }
        })
        .style('fill', function(d) {
          return d.data.data.image ? 'url(#' + md5(d.data.data.name) + ')' : '#cccccc';
        })
        .on('mouseover', function(d) {
          self.svg.select('g.node').each(function() {
            self.unhighlight(this);
          });

          if (!!d.data.data.details) {
            self.highlight(this.parentNode);
          }
        })
        .on('mouseout', function(d) {
          self.unhighlight(this.parentNode);
        })
        .on('click', function(d) {
          if (!!d.children || !!d._children) {
            self.unhighlight(this);
            self.click(d);
          }
        }); 
      
      nodeEnter.each(function() {
        self.unhighlight(this);
      });
      
      var nodeUpdate = nodeEnter.merge(node);

      nodeUpdate.transition().duration(self.options.duration)
        .attr('transform', function(d) {
          return 'translate(' + (d.x + self.options.margin.horizontal) + ',' + (d.y + self.options.margin.vertical) + ')';
        });

      nodeUpdate.select('circle.element')
        .attr('r', function(d) { return (!!d.children || !!d._children) ? 24 : 24.5; })
        .style('fill', function(d) {
          return d.data.data.image ? 'url(#' + md5(d.data.data.name) + ')' : '#efefef';
        });

      nodeUpdate.selectAll('text.label')
        .call(self.wrap, Math.round(nodeWidth))
        .each(function(d) {
          var bbox = this.getBBox();
          var offset = d.children || d._children ? (Math.round(bbox.height) + 24) * -1 : 38;
          d3.select(this).style('transform', 'translateY(' + offset + 'px)');
        });

      var nodeExit = node.exit()
        .transition().duration(self.options.duration)
        .attr('transform', function(d) {
          var p = null, n = d.parent;

          while (!!n) {
            if (!n.children && !!n._children) {
              p = n;
            }

            n = n.parent;
          }

          return 'translate(' + (p.x + self.options.margin.horizontal) + ',' + (p.y + self.options.margin.vertical) + ')';
        })
        .remove();

      nodeExit.select('circle')
        .attr('r', 1e-6);

      nodeExit.select('text.label')
        .style('fill-opacity', 1e-6);

      var links = $.map(treeData.descendants().slice(1), function(node) {
        return { node: node, parent: node.parent, related: false };
      });

      var visibleNodes = [];

      node.each(function(d) {
        visibleNodes.push(d.data.data.name);
      });

      nodeEnter.each(function(d) {
        visibleNodes.push(d.data.data.name);
      });

      $.each(treeData.descendants().slice(1), function(k, node) {
        $.each(node.data.data.related || [], function(k, r) {
          nodes.forEach(function(p) {
            if (p.data.id === r && $.inArray(p.data.id, visibleNodes) !== -1 && $.inArray(r, visibleNodes) !== -1) {
              links.push({ node: node, parent: p, related: true });
            }
          });
        });
      });

      var link = self.g.selectAll('path.link')
        .data(links, function(d) { return d.node.id + '/' + d.parent.id; });

      var linkEnter = link.enter().insert('path', 'g')
        .attr('class', function(d) {
          if (d.related) {
            return 'link related';
          } else {
            return 'link';
          }
        })
        .attr('d', function(d) {
          var o = { x: source.x0 + self.options.margin.horizontal, y: source.y0 + self.options.margin.vertical };
          return self.diagonal(o, o);
        });

      var linkUpdate = linkEnter.merge(link);

      linkUpdate.transition().duration(self.options.duration)
        .attr('d', function(d) { return self.diagonal(d.node, d.parent); });

      var linkExit = link.exit()
        .transition().duration(self.options.duration)
        .attr('d', function(d) {
          var p = null, n = d.parent;

          while (!!n) {
            if (!n.children && !!n._children) {
              p = n;
            }

            n = n.parent;
          }

          if (!p) {
            p = source;
          }

          var o = { x: p.x, y: p.y };

          return self.diagonal(o, o);
        })
        .remove();

      nodes.forEach(function(d) {
        d.x0 = d.x + self.options.margin.horizontal;
        d.y0 = d.y + self.options.margin.vertical;
      });
    };
    
    this.set = function(dataset) {
      self.svg.html(null);
      
      var data = d3.stratify()
        .id(function(d) { return d.name; })
        .parentId(function (d) { return d.parent; })
        (dataset);
        
      var defs = self.svg.append('svg:defs');
      
      $.each(data.descendants(), function(i, node) {
        if (node.data.image) {
          defs
            .append('svg:pattern')
            .attr('id', md5(node.id))
            .attr('patternContentUnits', 'objectBoundingBox')
            .attr('width', '100%')
            .attr('height', '100%')
            .append('svg:image')
            .attr('xlink:href', node.data.image)
            .attr('preserveAspectRatio', 'xMidYMid slice')
            .attr('width', 1)
            .attr('height', 1);
        }
      });
      
      self.g = self.svg.append('g')
        .attr('transform', 'translate(0, ' + self.options.margin.vertical + ')');

      self.treeMap = d3.tree().size([
        self.width - self.options.margin.horizontal * 2,
        self.height - self.options.margin.vertical * 2
      ]).nodeSize([96, 96]);

      self.root = d3.hierarchy(data, function(d) { return d.children; });
      self.root.x0 = self.width / 2;
      self.root.y0 = 0;
      
      self.root.children.forEach(self.collapse);
      
      self.refresh();
    };
    
    this.refresh = function() {
      self.update(self.root);
    };
    
  }
  
  $(document).on('ready', function() {
    
    $.get('./data/organisation.json').done(function(dataset) {
      var years = $.map(dataset, function(dataset, index) {
        return index;
      });
      
      var defaultYear = years[years.length - 1];
      var currentYear = null;
      
      var sections = $('#contains-organigramma-chart .contains-sections');
      
      var chart = new OrganizationChart({
        container: $('#contains-organigramma-chart'),
        margin: {
          horizontal: 120,
          vertical: 64
        },
        defaultHeight: 480,
        duration: 500,
        levelHeight: 320
      });
      
      function createHelp() {
        Help.add({
          handler: function() {
            var rects = $(_.sortBy($('#contains-organigramma-chart svg circle.element.has-children'), function(t) { return $(t).offset().left; }));

            var foundRect = $(rects[Math.ceil(rects.length * 0.66)]);

            var rect = foundRect[0].getBoundingClientRect();

            return {
              x: foundRect.offset().left + (rect.width / 2) - 32,
              y: foundRect.offset().top + (rect.height / 2) - 32,
              w: 64,
              h: 64
            };
          },
          alignment: 'right',
          rounded: true,
          text: Contents.organisation.help.expand
        });
      }
      
      function updateYear(year) {
        currentYear = year;
        
        var data = dataset[currentYear];
        
        sections.empty();
        
        $.each(data['sections'] || [], function(i, section) {
          if (!!section['elements'] && section.elements.length > 0) {
            var data = $.extend(section, {
              undefined: ($.grep(section.elements, function(e) { return !e.gender; }).length / section.elements.length) * 100,
              male: ($.grep(section.elements, function(e) { return !!e.gender && e.gender === 'male'; }).length / section.elements.length) * 100,
              female: ($.grep(section.elements, function(e) { return !!e.gender && e.gender === 'female'; }).length / section.elements.length) * 100
            });
            
            if (!!data['elements']) {
              data.elements = $.map(data.elements, function(element) {
                return $.extend(element, {
                  isMale: !!element.gender && element.gender === 'male',
                  isFemale: !!element.gender && element.gender === 'female',
                  isUndefined: !element.gender,
                  tooltip: Mustache.render($('#organisation-tooltip-template').html(), element)
                });
              });
            }
            
            var column = $(Mustache.render($('#organisation-section-template').html(), data));
            
            sections.append(column);
            
            column.find('span.count').each(function() {
              $(this).animateNumber({
                number: $(this).attr('data-value')
              });
            });
          }
        });
        
        chart.set(data['overview'] || []);
        
        if (Help.isEnabled()) {
          setTimeout(createHelp, 600);
        }

        $('body').on('help', createHelp);
        
        var index = $.inArray(String(year), years);
        
        $('#contains-organigramma-chart .contains-year-switcher .year').text(currentYear);
        $('#contains-organigramma-chart .contains-year-switcher .previous').toggleClass('disabled', index === 0 ? true : false);
        $('#contains-organigramma-chart .contains-year-switcher .next').toggleClass('disabled', index === (years.length - 1) ? true : false);
      }
      
      $(document).on('click', '#contains-organigramma-chart .contains-year-switcher .previous:not(.disabled)', function() {
        var index = $.inArray(String(currentYear), years);
        if (index > 0) {
          updateYear(years[index - 1]);
        }
      });
      
      $(document).on('click', '#contains-organigramma-chart .contains-year-switcher .next:not(.disabled)', function() {
        var index = $.inArray(String(currentYear), years);
        if (index < (years.length - 1)) {
          updateYear(years[index + 1]);
        }
      });
      
      $('#contains-organigramma-chart .contains-year-switcher .year').text(defaultYear);
      $('#contains-organigramma-chart .contains-year-switcher .previous').addClass('disabled');
      $('#contains-organigramma-chart .contains-year-switcher .next').addClass('disabled');
      
      var unhighlightTimeout = null;
      
      $(document).on('mouseover', '#contains-organigramma-chart .contains-sections ul li', function() {
        if (!!unhighlightTimeout) {
          clearTimeout(unhighlightTimeout);
        }
        
        $('#contains-organigramma-chart .contains-sections ul li.is-highlighted').removeClass('is-highlighted');
        
        $(this).addClass('is-highlighted');
      });
      
      $(document).on('mouseout', '#contains-organigramma-chart .contains-sections ul li', function() {
        unhighlightTimeout = setTimeout(function() {
          $('#contains-organigramma-chart .contains-sections ul li.is-highlighted').removeClass('is-highlighted');
        }, 750);
      });
      
      new Waypoint({
        offset: '25%',
        element: $('#contains-organigramma-chart')[0],
        handler: function() {
          updateYear(defaultYear);
          
          $(window).on('resize', function() {
            chart.refresh();
          });
          
          this.disable();
        }
      });
      
    });
    
  });
  
})(jQuery);