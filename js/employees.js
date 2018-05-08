/* global Contents, d3, Help, Mustache, screenfull, Waypoint */
;(function($) {
  
  function EmployeesChart(options) {

    var self = this;
    
    this.options = options;
    this.root = null;
    this.node = null;
    
    this.options.sizes = $.map(this.options.sizes, function(value) {
      return self.options.width * value;
    });

    self.radius = Math.min(self.options.width, self.options.height) / 2;

    self.svg = d3.select($(self.options.container).get(0))
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .attr('viewBox', '0 0 ' + self.options.width + ' ' + self.options.height)
      .append('g')
      .attr('transform', 'translate(' + (self.options.width / 2) + ',' + (self.options.shape === 'full' ? self.options.height / 2 : self.options.height) + ')rotate(' + (self.options.shape === 'full' ? '0' : '-90') + ')');

    self.tooltip = d3.select('#contains-employees')
      .append('div')
      .attr('id', 'sunburst-tooltip')
      .style('opacity', 0);

    self.partition = d3.partition();

    self.x = d3.scaleLinear().range([0, self.options.shape === 'full' ? 2 * Math.PI : 1 * Math.PI]);

    self.y = d3.scaleSqrt().range([0, self.radius]);

    self.defaultArc = d3.arc()
      .startAngle(function(d) {
        return Math.max(0, Math.min(self.options.shape === 'full' ? 2 * Math.PI : 1 * Math.PI, self.x(d.x0)));
      })
      .endAngle(function(d) {
        return Math.max(0, Math.min(self.options.shape === 'full' ? 2 * Math.PI : 1 * Math.PI, self.x(d.x1)));
      })
      .innerRadius(function(d) {
        var value = 0;
        if (d.depth > 0) {
          value = self.options.sizes.slice(0, d.depth).reduce(function(t, v) {
            return t + v;
          });
        }

        return Math.max(0, value / 2);
      })
      .outerRadius(function(d) {
        var value = self.options.sizes[d.depth];
        if (d.depth > 0) {
          value = self.options.sizes.slice(0, d.depth + 1).reduce(function(t, v) {
            return t + v;
          });
        }

        return Math.max(0, value / 2);
      });

    self.genderArc = d3.arc()
      .startAngle(function(d) {
        return self.defaultArc.startAngle()(d);
      })
      .endAngle(function(d) {
        return self.defaultArc.endAngle()(d);
      })
      .innerRadius(function(d) {
        var radius = self.defaultArc.innerRadius()(d);

        var scope = (d.data.default || d.data);
        if (scope.totale > 0) {
          radius += (((scope.totale_uomini / (scope.totale_uomini + scope.totale_donne)) * self.options.sizes[d.depth]) / 2);
        }
        
        return radius;
      })
      .outerRadius(function(d) {
        return self.defaultArc.outerRadius()(d);
      });

    this.slugify = function(text) {
      return text.toString().toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^\w\-]+/g, '')
        .replace(/\-\-+/g, '-')
        .replace(/^-+/, '')
        .replace(/-+$/, '');
    };

    this.pathForNode = function(node) {
      var parts = [];

      var n = node;
      while (n.depth > 0) {
        parts.push(self.slugify(n.data.name));
        n = n.parent;
      }

      return parts.reverse().join('/');
    };

    this.augmentDataset = function(node) {
      if (!!node.poli) {
        return $.extend(node, {
          children: $.map(node.poli, self.augmentDataset)
        });
      }

      if (!!node.centri) {
        return $.extend(node, {
          children: $.map(node.centri, self.augmentDataset)
        });
      }

      if (!!node.aree) {
        return $.extend(node, {
          children: $.map(node.aree, function(child, key) {
            var children = [];

            if (!!child.collaborazione_coordinata_jobs_act) {
              children.push($.extend(child.collaborazione_coordinata_jobs_act, {
                'type': 'cocojobsact',
                'name': Contents.employees.contracts.collaborazione_coordinata_jobs_act
              }));
            }

            if (!!child.tempo_indeterminato) {
              children.push($.extend(child.tempo_indeterminato, {
                'type': 'indeterminato',
                'name': Contents.employees.contracts.tempo_indeterminato
              }));
            }

            if (!!child.tempo_determinato) {
              children.push($.extend(child.tempo_determinato, {
                'type': 'determinato',
                'name': Contents.employees.contracts.tempo_determinato
              }));
            }

            if (!!child.borsa_di_dottorato) {
              children.push($.extend(child.borsa_di_dottorato, {
                'type': 'dottorato',
                'name': Contents.employees.contracts.borsa_di_dottorato
              }));
            }
            
            if (key === 'amministrazione') {
              return $.extend(child, {
                name: Contents.employees.areas.amministrazione,
                children: children
              });
            }
            
            if (key === 'ricerca') {
              return $.extend(child, {
                name: Contents.employees.areas.ricerca,
                children: children
              });
            }
            
            if (key === 'supporto_alla_ricerca') {
              return $.extend(child, {
                name: Contents.employees.areas.supporto_alla_ricerca,
                children: children
              });
            }
          })
        });
      }
      
      return node;
    };

    this.aggregate = function(gender, type, node) {
      if (!node) node = self.node;

      if (!!node.children) {
        var value = 0;

        $.each(node.children, function (i, c) {
          value += self.aggregate(gender, type, c);
        });

        return value;
      } else {
        var scope = {};

        if (!type || type === node.data.type) {
          scope = node.data.default || node.data;
        }
        
        if (type === 'foreigners' && !!node.data['stranieri']) {
          scope = node.data.stranieri;
        }

        if (type === 'protected' && !!node.data['categoria_protetta']) {
          scope = node.data.categoria_protetta;
        }

        if (!!gender && gender === 'male') {
          return scope.totale_uomini || 0;
        }

        if (!!gender && gender === 'female') {
          return scope.totale_donne || 0;
        }

        return scope.totale || 0;
      }
    };

    this.tweenPath = function(a, i, c) {
      var oi = d3.interpolate({ x0: (a.x0s ? a.x0s : 0), x1: (a.x1s ? a.x1s : 0), y0: (a.y0s ? a.y0s : 0), y1: (a.y1s ? a.y1s : 0) }, a);
        function tween(t) {
          var b = oi(t);
          a.x0s = b.x0;
          a.x1s = b.x1;
          a.y0s = b.y0;
          a.y1s = b.y1;

          return c(b);
        }

        if (i === 0 && self.node) {
          var xd = d3.interpolate(self.x.domain(), [self.node.x0, self.node.x1]);
          var yd = d3.interpolate(self.y.domain(), [self.node.y0, 1]);
          var yr = d3.interpolate(self.y.range(), [self.node.y0 ? 40 : 0, self.radius]);

          return function (t) {
            self.x.domain(xd(t));
            self.y.domain(yd(t)).range(yr(t));

            return tween(t);
          };
        } else {
            return tween;
        }
    };

    this.tweenText = function(a, i) {
      var oi = d3.interpolate({ x0: (a.x0s ? a.x0s : 0), x1: (a.x1s ? a.x1s : 0), y0: (a.y0s ? a.y0s : 0), y1: (a.y1s ? a.y1s : 0) }, a);

      function tween(t) {
        var b = oi(t);
        var angle = ((self.x((b.x0 + b.x1) / 2) - Math.PI / 2) / Math.PI * 180);
        b.textAngle = (angle > 90) ? 180 + angle : angle;
        a.centroid = self.defaultArc.centroid(b);
        return 'translate(' + self.defaultArc.centroid(b) + ')rotate(' + b.textAngle + ')';
      }

      return tween;
    };

    this.zoomToNode = function(node) {
      self.node = node;

      self.svg
        .transition()
        .duration(self.options.transitions)
        .tween('scale', function() {
          var xd = d3.interpolate(self.x.domain(), [self.node.x0, self.node.x1]);
          var yd = d3.interpolate(self.y.domain(), [self.node.y0, 1]);
          var yr = d3.interpolate(self.y.range(), [self.node.y0 ? 32 : 0, self.radius]);

          return function(t) { self.x.domain(xd(t)); self.y.domain(yd(t)).range(yr(t)); };
        })
        .selectAll('path.base')
        .attrTween('d', function(d) {
          return function() {
            return self.defaultArc(d);
          };
        });

      self.svg
        .transition()
        .duration(self.options.transitions)
        .tween('scale', function() {
          var xd = d3.interpolate(self.x.domain(), [self.node.x0, self.node.x1]);
          var yd = d3.interpolate(self.y.domain(), [self.node.y0, 1]);
          var yr = d3.interpolate(self.y.range(), [self.node.y0 ? 32 : 0, self.radius]);

          return function(t) {
            self.x.domain(xd(t));
            self.y.domain(yd(t)).range(yr(t));
          };
        })
        .selectAll('path.gender')
        .attrTween('d', function(d) {
          return function() {
            return self.genderArc(d);
          };
        });

      self.svg
        .selectAll('text')
        .transition('zoom')
        .duration(self.options.transitions)
        .attrTween('transform', function (d, i) {
          return self.tweenText(d, i);
        })
        .attr('text-anchor', function(d) {
          return d.textAngle > 180 ? 'end' : 'start';
        })
        .attr('dx', function (d) {
          return ((self.options.sizes[d.depth] / -4) + 4) * (d.textAngle > 180 ? -1 : +1);
        })
        .attr('dy', '.33em')
        .attr('opacity', function (e) {
          if (e.x0 >= (self.node.x0 - 0.0000000000001) && e.x1 <= (self.node.x1 + 0.0000000000001)) {
              return (e.x1 - e.x0 >= ((self.node.x1 - self.node.x0) * 0.01) ? 1 : 0);
          }

          return 0;
        });

      if (!!self.options.onChange) self.options.onChange(self);
    };

    this.zoomToRoot = function() {
      self.zoomToNode(self.root);
    };
    
    this.highlight = function(d, path) {
      $(self.options.container).addClass('contains-highlights');
      $('path[data-path^="' + path + '"]').addClass('is-highlighted');

      var values = [];
      var value;

      value = self.aggregate('female', null, d);
      if (!!value) {
        values.push({ name: Contents.employees.tooltip.female, value: value });
      }

      value = self.aggregate('male', null, d);
      if (!!value) {
        values.push({ name: Contents.employees.tooltip.male, value: value });
      }

      value = self.aggregate(null, 'cocojobsact', d);
      if (!!value) {
        values.push({ name: Contents.employees.tooltip.cocojobsact, value: value });
      }

      value = self.aggregate(null, 'indeterminato', d);
      if (!!value) {
        values.push({ name: Contents.employees.tooltip.indeterminato, value: value });
      }

      value = self.aggregate(null, 'determinato', d);
      if (!!value) {
        values.push({ name: Contents.employees.tooltip.determinato, value: value });
      }

      value = self.aggregate(null, 'dottorato', d);
      if (!!value) {
        values.push({ name: Contents.employees.tooltip.dottorato, value: value });
      }

      value = self.aggregate(null, 'foreigners', d);
      if (!!value) {
        values.push({ name: Contents.employees.tooltip.foreigners, value: value });
      }

      value = self.aggregate(null, 'protected', d);
      if (!!value) {
        values.push({ name: Contents.employees.tooltip.protected, value: value });
      }

      self.tooltip.html(Mustache.render($('#employees-tooltip-template').html(), {
        title: d.data.name.toUpperCase(),
        values: values
      }));

      var centroid = self.defaultArc.centroid(d);

      var tx = 0, ty = 0;

      if (self.options.shape === 'half') {
        tx = ((centroid[1] + (self.options.width / 2)) / self.options.width) * $(self.options.container).width();
        ty = ((self.options.height - centroid[0]) / self.options.height) * $(self.options.container).height();
        ty += 64;
      }

      if (self.options.shape === 'full') {
        tx = (((centroid[0] + (self.options.width / 2)) / self.options.width) * $(self.options.container).width()) + (($(self.options.container).parent().width() - $(self.options.container).width()) / 2);
        ty = (((centroid[1] + (self.options.height / 2)) / self.options.height) * $(self.options.container).height()) + (($(self.options.container).parent().height() - $(self.options.container).height()) / 2);
      }

      self.tooltip
        .transition()
        .duration(250)
        .style('opacity', 1.0)
        .style('left', tx + 'px')
        .style('top', ty + 'px');
    };
    
    this.unhighlight = function() {
      if ($(self.options.container).hasClass('contains-highlights')) {
        $(self.options.container).removeClass('contains-highlights');
        $('path.is-highlighted').removeClass('is-highlighted');

        self.tooltip
          .transition()
          .duration(250)
          .style('opacity', 0.0);
      }
    };
    
    this.showYear = function(year, callback) {
      self.svg
        .selectAll('g')
        .remove();
      
      if (!!self.options.data[year]) {
        var dataset = self.augmentDataset(self.options.data[year]);

        self.root = d3.hierarchy(dataset)
          .sum(function (d) {
            var scope = (d.default || d);
            return !d.children || d.children.length === 0 ? scope.totale : 0;
          });

        self.node = self.root;

        var group = self.svg
          .selectAll('g')
          .data(self.partition(self.root).descendants())
          .enter()
          .append('g');

        group
          .exit()
          .remove();

        group
          .append('path')
          .attr('d', self.defaultArc)
          .attr('display', function (d) {
            return d.depth ? null : 'none';
          })
          .attr('data-path', function (d) {
            return self.pathForNode(d);
          })
          .attr('class', function (d) {
            var classes = [];
            classes.push('base');
            classes.push('at-depth-' + d.depth);

            if (d.depth > 0 && d.depth <= 4) {
              var subRoot = d;
              while (subRoot.depth > 1) {
                subRoot = subRoot.parent;
              }

              classes.push('is-' + self.slugify(subRoot.data.name));

              var n = d.parent;
              while (n.depth > 1) {
                classes.push('child-of-' + self.slugify(n.data.name));
                n = n.parent;
              }
            }

            if (d.depth === 4) {
              classes.push('male');
            }

            return classes.join(' ');
          })
          .style('cursor', function (d) {
            return !!d.depth && (d.depth === 1 || d.depth === 2 || d.depth === 3 || d.depth === 4) ? 'pointer' : null;
          })
          .on('mouseover', function(d) {
            if (d.depth === 1 || d.depth === 2 || d.depth === 3 || d.depth === 4) {
              self.highlight(d, $(this).data('path'));
            }
          })
          .on('mouseout', function(d) {
              self.unhighlight();
          })
          .on('click', function(d) {
            if (d.depth === 1 || d.depth === 2 || d.depth === 3) {
              self.zoomToNode(d);
            }
          });

        group.each(function(d) {
          if (d.depth === 4) {
            d3.select(this)
              .append('path')
              .attr('d', self.genderArc(d))
              .attr('data-path', function (d) {
                return self.pathForNode(d);
              })
              .attr('class', function (d) {
                var classes = [];
                classes.push('gender');
                classes.push('female');
                classes.push('at-depth-' + d.depth);

                if (d.depth > 0 && d.depth <= 4) {
                  var subRoot = d;
                  while (subRoot.depth > 1) {
                    subRoot = subRoot.parent;
                  }

                  if (d.depth === 1) {
                    classes.push(self.slugify(subRoot.data.name));
                  } else {
                    classes.push('is-' + self.slugify(subRoot.data.name));

                    var n = d.parent;
                    while (n.depth > 1) {
                      classes.push('child-of-' + self.slugify(n.data.name));
                      n = n.parent;
                    }
                  }
                }

                return classes.join(' ');
              })
              .on('mouseover', function(d) {
                self.highlight(d, $(this).data('path'));
              })
              .on('mouseout', function(d) {
                self.unhighlight();
              });
          }
        });

        group
          .append('text')
          .attr('display', function (d) {
            return !!d.depth && d.depth > 1 ? null : 'none';
          })
          .text(function(d) {
            var name = d.data.name.toUpperCase();

            var maximumLength = (self.options.sizes[d.depth] / 5.5) - 1;
            if (name.length > maximumLength) {
              return name.substr(0, maximumLength - 2) + '..';
            }

            return name;
          })
          .each(function(d) {
            var angle = ((self.x((d.x0 + d.x1) / 2) - Math.PI / 2) / Math.PI * 180);
            d.textAngle = (angle > 90) ? 180 + angle : angle;
          })
          .transition('init')
          .duration(self.options.transitions)
          .attrTween('transform', function (d, i) {
            return self.tweenText(d, i);
          })
          .attr('text-anchor', function(d) {
            return d.textAngle > 180 ? 'end' : 'start';
          })
          .attr('dx', function (d) {
            return ((self.options.sizes[d.depth] / -4) + 4) * (d.textAngle > 180 ? -1 : +1);
          })
          .attr('dy', '.33em')
          .attr('opacity', function (e) {
            return (e.x1 - e.x0 >= 0.01 ? 1 : 0);
          })
          .attr('class', function (d) {
            return 'at-depth-' + d.depth;
          });

        self.svg
          .selectAll('path.base')
          .transition('init')
          .duration(self.options.transitions)
          .attrTween('d', function (d, i) {
            return self.tweenPath(d, i, self.defaultArc);
          });

        self.svg
          .selectAll('path.gender')
          .transition('init')
          .duration(self.options.transitions)
          .attrTween('d', function (d, i) {
            return self.tweenPath(d, i, self.genderArc);
          });

        if (!!self.options.onChange) self.options.onChange(self);

        if (!!callback) callback();
      }
    };
    
    this.showPreviousYear = function(callback) {
      var years = $.map(self.options.data, function(element, index) {
        return index;
      });

      var index = $.inArray(String(self.root.data.anno), years);
      if (index > 0) {
        self.showYear(years[index - 1], callback);
      }
    };
    
    this.showNextYear = function(callback) {
      var years = $.map(self.options.data, function(element, index) {
        return index;
      });

      var index = $.inArray(String(self.root.data.anno), years);
      if (index < (years.length - 1)) {
        self.showYear(years[index + 1], callback);
      }
    };
    
    this.refresh = function(delta, defaultYear) {
      self.options = $.extend(self.options, delta);
      
      self.x = d3.scaleLinear().range([0, self.options.shape === 'full' ? 2 * Math.PI : 1 * Math.PI]);
      
      self.svg
        .selectAll('g')
        .remove();
      
      self.svg = d3.select($(self.options.container).get(0))
        .attr('preserveAspectRatio', 'xMidYMid meet')
        .attr('viewBox', '0 0 ' + self.options.width + ' ' + self.options.height)
        .append('g')
        .attr('transform', 'translate(' + (self.options.width / 2) + ',' + (self.options.shape === 'full' ? self.options.height / 2 : self.options.height) + ')rotate(' + (self.options.shape === 'full' ? '0' : '-90') + ')');
      
      self.showYear(!!self.root ? self.root.data.anno : defaultYear);
    };

  };

  function drawGenderDistributionChart(selector, male, female) {
    var element = $(selector);

    var mWidth = 0.0, fWidth = 0.0;

    if (!!male || !!female) {
      mWidth = ((male / (male + female)) * 100);
      fWidth = ((female / (male + female)) * 100);
    }

    var svg = d3.select(selector)
      .attr('width', '100%')
      .attr('height', element.height());

    var maleRect = svg.select('.male');

    if (!maleRect.size()) {
      svg.append('g')
        .classed('male', true)
        .append('rect')
        .attr('x', '0')
        .attr('y', '0')
        .attr('width', mWidth + '%')
        .attr('height', element.height());
    } else {
      maleRect.selectAll('rect')
        .transition()
        .duration(500)
        .attr('width', mWidth + '%');
    }

    var femaleRect = svg.select('.female');

    if (!femaleRect.size()) {
      svg.append('g')
        .classed('female', true)
        .append('rect')
        .attr('x', mWidth + '%')
        .attr('y', '0')
        .attr('width', fWidth + '%')
        .attr('height', element.height());
    } else {
      femaleRect.selectAll('rect')
        .transition()
        .duration(500)
        .attr('x', mWidth + '%')
        .attr('width', fWidth + '%');
    }
  }
  
  $.get('./data/employees.json').done(function(data) {
    var years = $.map(data, function(element, index) {
      return index;
    });

    var defaultYear = years[years.length - 1];

    var employees = new EmployeesChart({
      data: data,
      container: $('#sunburst-chart'),
      shape: 'half',
      width: 768,
      height: 384,
      sizes: [ (384 / 768), (24/ 768), (108 / 768), (108 / 768), (144 / 768) ],
      transitions: 750,
      onChange: function(instance) {
        $('#sunburst-center-main .current-year').text(instance.root.data.anno);

        if (!!instance.node.depth) {
          $('#sunburst-center-main').addClass('is-zoomed-in');
        } else {
          $('#sunburst-center-main').removeClass('is-zoomed-in');
        }

        var years = $.map(instance.options.data, function(element, index) {
          return index;
        });

        var index = $.inArray(String(instance.root.data.anno), years);

        $('#sunburst-center-main .button-less').toggleClass('disabled', index === 0 ? true : false);
        $('#sunburst-center-main .button-more').toggleClass('disabled', index === (years.length - 1) ? true : false);

        $('#sunburst-center-main .breadcrumbs').empty();

        var context = instance.node;
        var description;

        while (!!context && context.depth > 0) {
          var li = $('<li/>');
          li.text(context.data.name.toUpperCase());
          li.attr('title', context.data.name.toUpperCase());

          li.on('click', $.proxy(function() {
              instance.zoomToNode(this.destinationNode);
          }, {
              destinationNode: context
          }));

          $('#sunburst-center-main .breadcrumbs').prepend(li);
          
          var currentPath = instance.pathForNode(context);
          if (!description && !!Contents.employees.descriptions[currentPath]) {
            description = Contents.employees.descriptions[currentPath];
          }

          context = context.parent;
        }

        drawGenderDistributionChart(
          '#sunburst-center-main #chart-jobs-general',
          instance.aggregate('male', null),
          instance.aggregate('female', null)
        );

        $('#sunburst-center-main h2').animateNumber({
          number: instance.aggregate(null, null)
        });
        
        if (!!description) {
          $('#employees-description').text(description);
        } else {
          $('#employees-description').html('&nbsp;');
        }

        var count, values;

        count = instance.aggregate(null, null);

        $('#sunburst-center-sub .contains-jobs-act-chart h1').animateNumber({ number: count });

        count = instance.aggregate(null, 'cocojobsact');

        values = (instance.node.data.collaborazione_coordinata_jobs_act || instance.node.data.contratti.collaborazione_coordinata_jobs_act || []);
        values = values.default || values;

        $('#sunburst-center-sub .contains-jobs-act-chart').toggleClass('is-undefined', !count);

        $('#sunburst-center-sub *[data-inject="cocojobsact/count"]').animateNumber({
          number: count
        });
        
        $('#sunburst-center-sub *[data-inject="cocojobsact/age"]').animateNumber({
          number: values.etamedia || 0
        });

        $('#sunburst-center-sub *[data-inject="cocojobsact/age/men"]').animateNumber({
          number: values.etamedia_uomini || 0
        });

        $('#sunburst-center-sub *[data-inject="cocojobsact/age/women"]').animateNumber({
          number: values.etamedia_donne || 0
        });

        drawGenderDistributionChart(
          '#sunburst-center-sub .contains-jobs-act-chart svg',
          instance.aggregate('male', 'cocojobsact'),
          instance.aggregate('female', 'cocojobsact')
        );

        count = instance.aggregate(null, 'indeterminato');

        values = (instance.node.data.tempo_indeterminato || instance.node.data.contratti.tempo_indeterminato || []);
        values = values.default || values;

        $('#sunburst-center-sub .contains-indeterminato-chart').toggleClass('is-undefined', !count);

        $('#sunburst-center-sub *[data-inject="indeterminato/count"]').animateNumber({
          number: count
        });

        $('#sunburst-center-sub *[data-inject="indeterminato/age"]').animateNumber({
          number: values.etamedia || 0
        });

        $('#sunburst-center-sub *[data-inject="indeterminato/age/men"]').animateNumber({
          number: values.etamedia_uomini || 0
        });

        $('#sunburst-center-sub *[data-inject="indeterminato/age/women"]').animateNumber({
          number: values.etamedia_donne || 0
        });

        drawGenderDistributionChart(
          '#sunburst-center-sub .contains-indeterminato-chart svg',
          instance.aggregate('male', 'indeterminato'),
          instance.aggregate('female', 'indeterminato')
        );

        count = instance.aggregate(null, 'determinato');

        values = (instance.node.data.tempo_determinato || instance.node.data.contratti.tempo_determinato || []);
        values = values.default || values;

        $('#sunburst-center-sub .contains-determinato-chart').toggleClass('is-undefined', !count);

        $('#sunburst-center-sub *[data-inject="determinato/count"]').animateNumber({
          number: count
        });

        $('#sunburst-center-sub *[data-inject="determinato/age"]').animateNumber({
          number: values.etamedia || 0
        });

        $('#sunburst-center-sub *[data-inject="determinato/age/men"]').animateNumber({
          number: values.etamedia_uomini || 0
        });

        $('#sunburst-center-sub *[data-inject="determinato/age/women"]').animateNumber({
          number: values.etamedia_donne || 0
        });

        drawGenderDistributionChart(
          '#sunburst-center-sub .contains-determinato-chart svg',
          instance.aggregate('male', 'determinato'),
          instance.aggregate('female', 'determinato')
        );

        count = instance.aggregate(null, 'dottorato');

        values = (instance.node.data.borsa_di_dottorato || instance.node.data.contratti.borsa_di_dottorato || []);
        values = values.default || values;

        $('#sunburst-center-sub .contains-dottorandi-chart').toggleClass('is-undefined', !count);

        $('#sunburst-center-sub *[data-inject="phd/count"]').animateNumber({
          number: count
        });

        $('#sunburst-center-sub *[data-inject="phd/age"]').animateNumber({
          number: values.etamedia || 0
        });

        $('#sunburst-center-sub *[data-inject="phd/age/men"]').animateNumber({
          number: values.etamedia_uomini || 0
        });

        $('#sunburst-center-sub *[data-inject="phd/age/women"]').animateNumber({
          number: values.etamedia_donne || 0
        });

        drawGenderDistributionChart(
          '#sunburst-center-sub .contains-dottorandi-chart svg',
          instance.aggregate('male', 'dottorato'),
          instance.aggregate('female', 'dottorato')
        );

        count = instance.aggregate(null, 'foreigners');

        values = (instance.node.data.stranieri || []);

        $('#sunburst-center-sub .contains-stranieri-chart').toggleClass('is-undefined', !count);

        $('#sunburst-center-sub *[data-inject="foreigners/count"]').animateNumber({
          number: count
        });

        $('#sunburst-center-sub *[data-inject="foreigners/age"]').animateNumber({
          number: values.etamedia || 0
        });

        $('#sunburst-center-sub *[data-inject="foreigners/age/men"]').animateNumber({
          number: values.etamedia_uomini || 0
        });

        $('#sunburst-center-sub *[data-inject="foreigners/age/women"]').animateNumber({
          number: values.etamedia_donne || 0
        });

        drawGenderDistributionChart(
          '#sunburst-center-sub .contains-stranieri-chart svg',
          instance.aggregate('male', 'foreigners'),
          instance.aggregate('female', 'foreigners')
        );

        count = instance.aggregate(null, 'protected');

        values = (instance.node.data.categoria_protetta || []);

        $('#sunburst-center-sub .categoria-protetta-chart').toggleClass('is-undefined', !count);

        $('#sunburst-center-sub *[data-inject="protected/count"]').animateNumber({
          number: count
        });

        $('#sunburst-center-sub *[data-inject="protected/age"]').animateNumber({
          number: values.etamedia || 0
        });

        $('#sunburst-center-sub *[data-inject="protected/age/men"]').animateNumber({
          number: values.etamedia_uomini || 0
        });

        $('#sunburst-center-sub *[data-inject="protected/age/women"]').animateNumber({
          number: values.etamedia_donne || 0
        });

        drawGenderDistributionChart(
          '#sunburst-center-sub .contains-categoria-protetta-chart svg',
          instance.aggregate('male', 'protected'),
          instance.aggregate('female', 'protected')
        );
      }
    });
    
    function createHelp() {
      Help.add({
        selector: '#sunburst-center-main .button-less',
        alignment: 'left',
        rounded: true,
        text: Contents.employees.help.navigateYears
      });
      
      Help.add({
        selector: '#sunburst-center-main .current-year',
        alignment: 'right',
        text: Contents.employees.help.currentYear
      });
      
      Help.add({
        handler: function() {
          var chart = $('#sunburst-chart');
          
          return {
            x: chart.offset().left + (chart.width() * 0.75),
            y: chart.offset().top + (chart.height() * 0.50),
            w: 64,
            h: 64
          };
        },
        alignment: 'left',
        rounded: true,
        text: Contents.employees.help.expand
      });
      
      Help.add({
        handler: function() {
          var chart = $('#sunburst-chart');
          
          return {
            x: chart.offset().left + (chart.width() * 0.50),
            y: chart.offset().top + (chart.height() * 0.05),
            w: 64,
            h: 64
          };
        },
        alignment: 'right',
        rounded: true,
        text: Contents.employees.help.details
      });
    }
    
    new Waypoint({
      offset: '25%',
      element: $('#contains-sunburst-chart')[0],
      handler: function() {
        var years = $.map(data, function(element, index) {
          return index;
        });
        
        employees.showYear(years[years.length - 1], function() {
          $('#sunburst-chart').addClass('has-been-rendered');
          
          if (Help.isEnabled()) {
            setTimeout(function() {
              createHelp();
            }, 850);
          }
          
          $('body').on('help', createHelp);
          $('#contains-employees').on('help', createHelp);
        });

        this.disable();
      }
    });
    
    $(document).on('click', '#contains-employees *[data-action="toggle-fullscreen"]', function(e) {
      if (!!e.preventDefault) e.preventDefault();
      
      $('#contains-employees').toggleClass('is-fullscreen');

      if (screenfull.enabled) {
        screenfull.toggle($('#contains-employees')[0]);
      } else {
        $('#contains-employees').toggleClass('is-fallback-fullscreen');
        adaptToFullscreen();
      }

      return false;
    });
    
    function clearEmployeesFullscreenStyles() {
      $('#sunburst-chart').css('width', '');
      $('#sunburst-chart').css('height', '');

      $('#contains-employees-overview').css('transform', '');
      $('#contains-employees-overview').css('width', '');
      $('#contains-employees-overview').css('top', '');
      $('#contains-employees-overview').css('left', '');

      $('#contains-employees-overview').appendTo('#contains-employees');
      $('#sunburst-tooltip').appendTo('#contains-employees');
    }

    function adaptEmployeesWhenInFullscreen() {
      clearEmployeesFullscreenStyles();

      if (!$('#contains-employees-overview').data('originalWidth')) {
        $('#contains-employees-overview').data('originalWidth', $('#contains-employees-overview').width());
      }

      if (!$('#contains-employees-overview').data('originalHeight')) {
        $('#contains-employees-overview').data('originalHeight', $('#contains-employees-overview').height());
      }

      var size = Math.min(
        $('#contains-sunburst-chart').height(),
        $('#contains-sunburst-chart').width()
      );

      $('#sunburst-chart').css('width', size);
      $('#sunburst-chart').css('height', size);

      $('#contains-employees-overview').insertAfter('#sunburst-chart');
      $('#sunburst-tooltip').insertAfter('#sunburst-chart');

      var ratio = .40;
      var scale = ((size * ratio) / $('#contains-employees-overview').data('originalWidth'));

      $('#contains-employees-overview').css('transform', 'scale(' + scale + ')');
      $('#contains-employees-overview').css('width', (size * ratio) / scale);
      $('#contains-employees-overview').css('top', ($('#contains-sunburst-chart').height() - (size * ratio)) / 2);
      $('#contains-employees-overview').css('left', ($('#contains-sunburst-chart').width() - (size * ratio)) / 2);
    }

    function adaptEmployeesWhenInFullscreenOnOrientationChange() {
      setTimeout(function() {
        adaptEmployeesWhenInFullscreen();
      }, 500);
    }

    function adaptToFullscreen() {
      if ((screenfull.enabled && screenfull.isFullscreen) || $('#contains-employees').hasClass('is-fallback-fullscreen')) {
        employees.refresh({
          width: 768,
          height: 768,
          shape: 'full'
        }, defaultYear);

        setTimeout(function() {
          $(window).on('resize', adaptEmployeesWhenInFullscreen);
          $(window).on('orientationchange', adaptEmployeesWhenInFullscreenOnOrientationChange);

          adaptEmployeesWhenInFullscreen();
        }, 100);
      } else {
        $(window).off('resize', adaptEmployeesWhenInFullscreen);
        $(window).off('orientationchange', adaptEmployeesWhenInFullscreenOnOrientationChange);

        clearEmployeesFullscreenStyles();

        employees.refresh({
          width: 768,
          height: 384,
          shape: 'half'
        }, defaultYear);
        
        $('#contains-employees').removeClass('is-fullscreen');
        
        Help.close();
      }
    }

    if (screenfull.enabled) {
      screenfull.onchange(adaptToFullscreen);
    }

    $(document).on('click', '#contains-employees .button-less:not(.disabled)', function() {
      employees.showPreviousYear();
    });

    $(document).on('click', '#contains-employees .button-more:not(.disabled)', function() {
      employees.showNextYear();
    });

    $(document).on('click', '#contains-employees *[data-action="zoom-to-root"]', function() {
      employees.zoomToRoot();
    });
  });

})(jQuery);
