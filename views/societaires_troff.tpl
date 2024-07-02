% for item in data:
.datastart
	% for key in item:
		% if key == 'etiquettes':
.	ds {{key}} {{", ".join(item[key])}}
		% else:
.	ds {{key}} {{item[key]}}
		% end
	% end
	% for tag in meta:
		% if tag in item['etiquettes']:
.		nr {{tag}} 1
		% else:
.		nr {{tag}} 0
		% end
	%end
.datastop
% end
