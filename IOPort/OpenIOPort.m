function [portobject, address, status] = OpenIOPort( address )
%[portobject, address, status] = OpenIOPort( address )
%default port address is 53328
if nargin < 1
    address = hex2dec('C050');
end
portobject = io64;
if nargout > 1
    status = io64( portobject );
end
end