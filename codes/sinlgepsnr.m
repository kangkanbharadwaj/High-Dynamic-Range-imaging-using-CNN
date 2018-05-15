        

ref = imread('/misc/lmbraid18/bharadwk/test_hdr_rendered_image/ArlesRoom/hdr_image0001.png');
input = imread('/misc/lmbraid18/bharadwk/workspace/ws1/hdr_snapshot_iter_deformation_l2perloc_modelred2HALF/150000/paintroom.png'); 
ref = im2single(ref);
input = im2single(input);

numPixels = numel(input);
sqrdErr = sum((input(:) - ref(:)).^2) / numPixels;
disp(sqrdErr);
errEst = 10 * log10(1/sqrdErr);
disp(errEst);