/* global Contents, d3, Mustache, numeral, Waypoint */
;(function($) {
  
  var labels = Contents.balance.labels;
  
  function slugify(text) {
    return text.toString().toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^\w\-]+/g, '')
      .replace(/\-\-+/g, '-')
      .replace(/^-+/, '')
      .replace(/-+$/, '');
  };
  
  function highlight(container, args, classes) {
    $(container).removeClass('contains-highlighted');
    
    $(container).find('.is-highlighted').removeClass('is-highlighted');
    
    if (!!$(container).data('highlight-classes')) {
      $(container).data('highlight-classes').forEach(function(c) {
        $(container).removeClass(c);
      });
    }
    
    $(container).data('highlight-classes', null);
    
    if (args !== false && !!args) {
      if (args.constructor === Object) {
        args = [ args ];
      }
      
      $(container).find($.map(args, function(arg) {
        return '*' + $.map(arg, function(value, key) {
          return '[data-' + key + '*="' + value + '"]';
        }).join('');
      }).join(',')).addClass('is-highlighted');
      
      $(container).addClass('contains-highlighted');
      
      if (!!classes) {
        classes.forEach(function(c) {
          $(container).addClass(c);
        });
        
        $(container).data('highlight-classes', classes);
      }
    }
  }
  
  var $tooltip = $('<div/>');
  $tooltip.attr('id', 'balance-tooltip');
  $tooltip.css('visibility', 'hidden');
  $tooltip.appendTo('body');
  
  function tooltip(selector, contents) {
    if (contents === false) {
      $(selector).css('visibility', 'hidden');
    } else {
      $(selector).empty().html(contents);

      updateTooltip(selector);

      $(selector).css('visibility', 'visible');
    }
  }
  
  function updateTooltip(selector) {
    $(selector).css('top', (d3.event.pageY + 10) + 'px');
    $(selector).css('left', function() {
      return Math.min(Math.max(d3.event.pageX, 10), window.innerWidth - $(selector).width() - 20) + 'px';
    });
  }
  
  function centreTooltip(selector, d) {
    tooltip(selector, Mustache.render($('#bilancio-tooltip-template').html(), {
      name: d.name,
      incoming: $.map(d.sourceLinks.sort(function(a, b) { return b.value - a.value; }), function(link) {
        return { name: link.name, value: numeral(link.value).format('0,0') };
      }),
      outgoing: $.map(d.targetLinks.sort(function(a, b) { return b.value - a.value; }), function(link) {
        return { name: link.name, value: numeral(link.value).format('0,0') };
      }),
      sums: {
        incoming: numeral(d3.sum($.map(d.sourceLinks, function(link) { return link.value; }))).format('0,0'),
        outgoing: numeral(d3.sum($.map(d.targetLinks, function(link) { return link.value; }))).format('0,0')
      }
    }));
  }
  
  function incomeTooltip(selector, d) {
    tooltip(selector, Mustache.render($('#bilancio-tooltip-template').html(), {
      name: d.name,
      incoming: $.map(d.sourceLinks.sort(function(a, b) { return b.value - a.value; }), function(source) {
        return { name: source.target.name, value: numeral(source.value).format('0,0') };
      }),
      sums: {
        incoming: numeral(d3.sum($.map(d.sourceLinks, function(link) { return link.value; }))).format('0,0')
      }
    }));
  }
  
  function expenseTooltip(selector, d) {
    tooltip(selector, Mustache.render($('#bilancio-tooltip-template').html(), {
      name: d.name,
      outgoing: $.map(d.targetLinks.sort(function(a, b) { return b.value - a.value; }), function(target) {
        return { name: target.source.name, value: numeral(target.value).format('0,0') };
      }),
      sums: {
        outgoing: numeral(d3.sum($.map(d.targetLinks, function(link) { return link.value; }))).format('0,0')
      }
    }));
  }
  
  function sortedValuesByIndex(elements) {
    var values = [], index = {};
    
    elements.each(function(d) {
      values.push({ index: d.index, value: d.value });
    });
    
    values.sort(function(a, b) { return (b.value - a.value); }).forEach(function(v, i) {
      index[v.index] = i;
    });
    
    return index;
  }
  
  function drawBalanceOverviewChart(container, data, callback) {
    $(container).empty();
    
    var nodes = [];
    var links = [];
    
    var incomes = {};
    var totalIncomes = 0;
    
    var expenses = {};
    var totalExpenses = 0;
    
    $.each(data, function(key, values) {
      var index = nodes.length;
      
      nodes.push({
        context: [ md5(slugify(key)) ],
        triggers: md5(slugify(key)),
        hash: md5(slugify(key)),
        name: key
      });
      
      $.each(values.incoming, function(type, value) {
        var context = md5('incoming/' + slugify(type));
        
        if (!(type in incomes)) {
          incomes[type] = nodes.length;
          
          nodes.push({
            context: [ context ],
            triggers: context,
            type: 'incoming',
            hash: context,
            name: labels[type] || type
          });
        }
        
        links.push({
          context: [ md5(slugify(key)), context ],
          triggers: context,
          type: 'incoming',
          hash: context,
          name: labels[type] || type,
          source: incomes[type],
          target: index,
          value: value
        });
        
        totalIncomes += value;
      });
      
      $.each(values.expenses, function(type, value) {
        var context = md5('outgoing/' + slugify(type));
        
        if (!(type in expenses)) {
          expenses[type] = nodes.length;
          
          nodes.push({
            context: [ context ],
            triggers: context,
            type: 'outgoing',
            hash: context,
            name: labels[type] || type
          });
        }
        
        links.push({
          context: [ md5(slugify(key)), context ],
          triggers: context,
          hash: context,
          type: 'outgoing',
          name: labels[type] || type,
          source: index,
          target: expenses[type],
          value: value
        });
        
        totalExpenses += value;
      });
    });
    
    var graph = {
      nodes: nodes,
      links: links,
      sort: function() {
        return function(a, b) { return b.value - a.value; };
      }
    };
    
    var svg = d3.select(container)
      .append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .attr('viewBox', '0 0 1024 768');
    
    var sankey = d3.sankey()
      .nodeWidth(function(d) { return d.depth === 1 ? 192 : 8; })
      .nodePadding(10)
      .extent([[0, 16], [1024, 752]]);
    
    var link = svg.append('g')
      .attr('class', 'links')
      .attr('fill', 'none')
      .selectAll('path');
    
    var node = svg.append('g')
      .attr('class', 'nodes')
      .selectAll('g');
    
    sankey(graph);
    
    link = link
      .data(graph.links)
      .enter()
      .append('path')
      .attr('d', d3.sankeyLinkHorizontal())
      .attr('class', function(d) { return d.type; })
      .attr('stroke-width', function(d) { return Math.max(1, d.width); })
      .attr('stroke-dasharray', function(d) {
        var length = d3.select(this).node().getTotalLength();
        return length + ' ' + length;
      })
      .attr('stroke-dashoffset', function(d) { return d3.select(this).node().getTotalLength(); })
      .on('mouseout', function() {
        highlight(container, false);
        tooltip('#balance-tooltip', false);
      });
    
    link.filter(function(d) { return d.type === 'incoming'; })
      .attr('data-centre', function(d) { return d.target.hash; })
      .attr('data-income', function(d) { return d.hash; })
      .on('mouseover', function(d) {
        highlight(container, { income: d.hash }, ['is-highlighting-incomes']);
        incomeTooltip('#balance-tooltip', d.source);
      })
      .on('mousemove', function() { updateTooltip('#balance-tooltip'); });
    
    link.filter(function(d) { return d.type === 'outgoing'; })
      .attr('data-centre', function(d) { return d.source.hash; })
      .attr('data-expense', function(d) { return d.hash; })
      .on('mouseover', function(d) {
        highlight(container, { expense: d.hash }, ['is-highlighting-expenses']);
        expenseTooltip('#balance-tooltip', d.target);
      })
      .on('mousemove', function() { updateTooltip('#balance-tooltip'); });
    
    node = node
      .data(graph.nodes)
      .enter().append('g');
    
    node.filter(function(d) { return d.depth === 0; })
      .attr('data-income', function(d) { return d.hash; })
      .attr('data-centre', function(d) { return d.sourceLinks.map(function(l) { return l.target.hash; }).join(','); })
      .attr('class', 'io incoming')
      .attr('opacity', 0);
    
    node.filter(function(d) { return d.depth === 1; })
      .attr('data-centre', function(d) { return d.hash; })
      .attr('data-income', function(d) { return d.targetLinks.map(function(l) { return l.hash; }).join(','); })
      .attr('data-expense', function(d) { return d.sourceLinks.map(function(l) { return l.hash; }).join(','); })
      .attr('class', 'centre')
      .attr('opacity', 0);
    
    node.filter(function(d) { return d.depth === 2; })
      .attr('data-expense', function(d) { return d.hash; })
      .attr('data-centre', function(d) { return d.targetLinks.map(function(l) { return l.source.hash; }).join(','); })
      .attr('class', 'io incoming')
      .attr('opacity', 0);
    
    var rects = node.append('rect')
      .attr('x', function(d) { return d.x0; })
      .attr('y', function(d) { return d.y0; })
      .attr('width', function(d) { return d.x1 - d.x0; })
      .attr('height', function(d) { return d.y1 - d.y0; })
      .on('mouseout', function() {
        highlight(container, false);
        tooltip('#balance-tooltip', false);
      })
      .on('mousemove', function() { updateTooltip('#balance-tooltip'); });
    
    rects.filter(function(d) { return d.depth === 1; })
      .attr('class', 'base')
      .on('mouseover', function(d) {
        highlight(container, []
          .concat(d.targetLinks.map(function(l) { return { centre: d.hash, income: l.hash }; }))
          .concat(d.sourceLinks.map(function(l) { return { centre: d.hash, expense: l.hash }; })), ['is-highlighting-centres']);
        centreTooltip('#balance-tooltip', d);
    });
    
    rects.filter(function(d) { return (d.depth === 0 || d.depth === 2) && d.type === 'incoming'; })
      .on('mouseover', function(d) {
        highlight(container, { income: d.hash }, ['is-highlighting-incomes']);
        incomeTooltip('#balance-tooltip', d);
      });
    
    rects.filter(function(d) { return d.depth === 2 && d.type === 'outgoing'; })
      .on('mouseover', function(d) {
        highlight(container, { expense: d.hash }, ['is-highlighting-expenses']);
        expenseTooltip('#balance-tooltip', d);
      });
    
    node.filter(function(d) { return d.depth === 1; })
      .append('rect')
      .attr('class', 'incoming')
      .attr('x', function(d) { return d.x0; })
      .attr('y', function(d) { return d.y0; })
      .attr('width', 8)
      .attr('height', function(d) { return (d.y1 - d.y0); });
    
    node.filter(function(d) { return d.depth === 1; })
      .append('rect')
      .attr('class', 'outgoing')
      .attr('x', function(d) { return (d.x1 - 8); })
      .attr('y', function(d) { return d.y0; })
      .attr('width', 8)
      .attr('height', function(d) { return (d.y1 - d.y0); });
    
    var texts = node.append('text')
      .text(function(d) { return d.name; })
      .attr('y', function(d) { return (d.y1 + d.y0) / 2; })
      .attr('dy', '0.35em');

    texts
      .filter(function(d) { return d.depth === 0; })
      .attr('x', function(d) { return d.x1 + 6; })
      .attr('text-anchor', 'start');
    
    texts
      .filter(function(d) { return d.depth === 1; })
      .attr('x', function(d) { return d.x0 + ((d.x1 - d.x0) / 2); })
      .attr('text-anchor', 'middle');
    
    texts
      .filter(function(d) { return d.depth === 2; })
      .attr('x', function(d) { return d.x0 - 6; })
      .attr('text-anchor', 'end');
    
    var totalTransition = 250,
      linkTransition = 750,
      stepBase = 76,
      stepTransition = 24;
    
    var offset = 0;
    
    $('<div class="total incoming">&euro; ' + numeral(totalIncomes).format('0,0') + '</div>')
      .appendTo($(container))
      .fadeOut(0)
      .delay(offset)
      .fadeIn(totalTransition);
    
    offset += totalTransition;
    
    (function(index) {
      node.filter(function(d) { return d.depth === 0; })
        .transition()
        .duration(stepBase)
        .delay(function(d) { return offset + (index[d.index] * stepTransition); })
        .attr('opacity', 1);
    })(sortedValuesByIndex(rects.filter(function(d) { return d.depth === 0; })));
    
    offset += (stepBase + (texts.filter(function(d) { return d.depth === 0; }).size() * stepTransition));
    
    link.filter(function(d) { return d.type === 'incoming'; })
      .transition()
      .duration(linkTransition)
      .delay(offset)
      .attr('stroke-dashoffset', 0);
    
    offset += linkTransition;
    
    (function(index) {
      node.filter(function(d) { return d.depth === 1; })
        .transition()
        .duration(stepBase)
        .delay(function(d) { return offset + (index[d.index] * stepTransition); })
        .attr('opacity', 1);
    })(sortedValuesByIndex(rects.filter(function(d) { return d.depth === 1; })));
    
    offset += (stepBase + (texts.filter(function(d) { return d.depth === 1; }).size() * stepTransition));
    
    link.filter(function(d) { return d.type === 'outgoing'; })
      .transition()
      .duration(linkTransition)
      .delay(offset)
      .attr('stroke-dashoffset', 0);
    
    offset += linkTransition;
    
    (function(index) {
      node.filter(function(d) { return d.depth === 2; })
        .transition()
        .duration(stepBase)
        .delay(function(d) { return offset + (index[d.index] * stepTransition); })
        .attr('opacity', 1);
    })(sortedValuesByIndex(texts.filter(function(d) { return d.depth === 2; })));
    
    offset += (stepBase + (texts.filter(function(d) { return d.depth === 2; }).size() * stepTransition));
    
    $('<div class="total outgoing">&euro; ' + numeral(totalExpenses).format('0,0') + '</div>')
      .appendTo($(container))
      .fadeOut(0)
      .delay(offset)
      .fadeIn(totalTransition);
    
    offset += totalTransition;
    
    setTimeout(function() { if (!!callback) callback(); }, offset);
  }
  
  $(document).on('ready', function() {
    numeral.locale('it');
    
    $('.bilancio-chart-switcher').hide();
    
    $.get('./data/balance.json').done(function(data) {
      var container = $('#bilancio-chart').get(0);
      
      function createHelp() {
        Help.add({
          handler: function() {
            var firstCentre = $(_.min($('#bilancio-chart svg .centre text'), function(t) { return $(t).offset().top; }));
            
            var rect = firstCentre[0].getBoundingClientRect();

            return {
              x: firstCentre.offset().left,
              y: firstCentre.offset().top,
              w: rect.width,
              h: rect.height
            };
          },
          padding: [64, 32],
          alignment: 'right',
          text: Contents.balance.help.centre
        });
        
        Help.add({
          handler: function() {
            var firstRect = $(_.min($('#bilancio-chart svg g.io.incoming[data-income] rect'), function(t) { return $(t).offset().top; }));

            var rect = firstRect[0].getBoundingClientRect();

            return {
              x: firstRect.offset().left + (rect.width / 2) - 32,
              y: firstRect.offset().top + (rect.height / 2) - 32,
              w: 64,
              h: 64
            };
          },
          alignment: 'right',
          rounded: true,
          text: Contents.balance.help.incoming
        });
        
        Help.add({
          handler: function() {
            var rects = $(_.sortBy($('#bilancio-chart svg g.centre rect.incoming'), function(t) { return $(t).offset().top; }));
  
            var foundRect = $(rects[Math.ceil(rects.length * 0.50)]);
  
            var rect = foundRect[0].getBoundingClientRect();

            return {
              x: foundRect.offset().left + (rect.width / 2) - 32,
              y: foundRect.offset().top + (rect.height / 2) - 32,
              w: 64,
              h: 64
            };
          },
          alignment: 'left',
          rounded: true,
          text: Contents.balance.help.incoming
        });
        
        Help.add({
          handler: function() {
            var rects = $(_.sortBy($('#bilancio-chart svg g.centre rect.outgoing'), function(t) { return $(t).offset().top; }));

            var foundRect = $(rects[Math.ceil(rects.length * 0.25)]);

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
          text: Contents.balance.help.outgoing
        });
        
        Help.add({
          handler: function() {
            var rects = $(_.sortBy($('#bilancio-chart svg g.io.incoming[data-expense] rect'), function(t) { return $(t).offset().top; }));
  
            var foundRect = $(rects[Math.ceil(rects.length * 0.50)]);
  
            var rect = foundRect[0].getBoundingClientRect();

            return {
              x: foundRect.offset().left + (rect.width / 2) - 32,
              y: foundRect.offset().top + (rect.height / 2) - 32,
              w: 64,
              h: 64
            };
          },
          alignment: 'left',
          rounded: true,
          text: Contents.balance.help.outgoing
        });
      }
      
      new Waypoint({
        offset: '50%',
        element: container,
        handler: function() {
          var years = $.map(data, function(_, index) { return index; });
          
          var currentYear = years[years.length - 1];
          
          function updateButtons() {
            if (years.indexOf(currentYear) > 0) {
              $('.bilancio-chart-switcher .previous').removeClass('disabled');
            } else {
              $('.bilancio-chart-switcher .previous').addClass('disabled');
            }
            
            if (years.indexOf(currentYear) < (years.length - 1)) {
              $('.bilancio-chart-switcher .next').removeClass('disabled');
            } else {
              $('.bilancio-chart-switcher .next').addClass('disabled');
            }
          }
          
          $('.bilancio-chart-switcher').on('click', '.previous:not(.disabled)', function() {
            currentYear = years[years.indexOf(currentYear) - 1];
            
            $('.bilancio-chart-switcher .current-year').text(currentYear);
            drawBalanceOverviewChart(container, data[currentYear]);
            updateButtons();
          });
          
          $('.bilancio-chart-switcher').on('click', '.next:not(.disabled)', function() {
            currentYear = years[years.indexOf(currentYear) + 1];
            
            $('.bilancio-chart-switcher .current-year').text(currentYear);
            drawBalanceOverviewChart(container, data[currentYear]);
            updateButtons();
          });
          
          $('.bilancio-chart-switcher').show();
          
          $('.bilancio-chart-switcher .current-year').text(currentYear);
          
          drawBalanceOverviewChart(container, data[currentYear], function() {
            if (Help.isEnabled()) {
              createHelp();
            }

            $('body').on('help', createHelp);
          });
          
          updateButtons();
          
          this.disable();
        }
      });
      
      var centres = {};
      var range = { min: 0, max: 0 };

      $.each(data, function(year, dataset) {
        $.each(dataset, function(key, values) {
          var incoming = d3.sum($.map(values.incoming, function(value) { return value; }));
          var outgoing = d3.sum($.map(values.expenses, function(value) { return value; }));
          var value = (incoming - outgoing);

          range.min = Math.min(range.min, value);
          range.max = Math.max(range.max, value);

          if (!(key in centres)) {
            centres[key] = [];
          }

          centres[key].push({
            year: year,
            incoming: incoming,
            expenses: outgoing,
            value: value
          });
        });
      });
    });
  });
  
})(jQuery);