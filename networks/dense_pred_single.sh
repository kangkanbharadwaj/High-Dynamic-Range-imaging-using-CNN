#!/bin/bash

# Prepare environment
alias matlab="/misc/software/matlab/R2015a/bin/matlab"
LD_LIBRARY_PATH=/home/alis/caffe3D/release/lib:$LD_LIBRARY_PATH
LD_LIBRARY_PATH=/misc/software/matlab/R2015a/bin/matlab:$LD_LIBRARY_PATH

which caffe

train_file="/misc/lmbraid11/alis/2d_dense/2d_dense-train.prototxt";
snapshotdir='/misc/lmbraid11/alis/2d_dense';
input_data="/misc/lmbraid11/alis/2d_dense/test/15_05ng_hNRIP1_wt_links_63x_embryo02.h5";
NETNAME="2d_dense";
snapshot="2d_dense_snapshot_iter_400000.caffemodel.h5";

if [ -e ${snapshotdir}/${snapshot} ]; then
    sed -e "s+@scriptname@+${0}+g" \
	-e "s+@train_file@+${train_file}+g" \
	-e "s+@test_file@+${test_file}+g" \
	-e "s+@snapshotdir@+${snapshotdir}+g" \
	-e "s+@input_data@+${input_data}+g" \
	-e "s+@datadir@+${datadir}+g" \
	-e "s+@NETNAME@+${NETNAME}+g" \
	-e "s/@snapshot@/${snapshot}/g" > dense_pred.m <<EOF

%% setup environment
addpath('/home/alis/caffe3D/matlab');

try 
  caffe.set_mode_gpu();
  caffe.set_device(0);
catch e
  caffe.set_mode_cpu();
end

fid            = fopen('@train_file@');
train_prototxt = fread(fid);
fclose(fid);

% data: input data
data = ncread('@input_data@','data');

% dim: dimensions of data, input, and output
dim.bottom = [9 9];
dim.data = [1936 1460 1];
%3-3-3 / 3-3-3
scalefun   = @(x) deal([(((((((x(1)+4)*2)+4)*2)+4)*2)+4) (((((((x(2)+4)*2)+4)*2)+4)*2)+4)], ...
                       [((((((x(1)*2)-4)*2)-4)*2)-4) ((((((x(2)*2)-4)*2)-4)*2)-4)]);
[dim.input dim.output] = scalefun(dim.bottom);
dim.tiles = ceil(dim.data(1:2)./dim.output);
dim.min_offset = -[(dim.input(1)-dim.output(1))/2 ...
               (dim.input(2)-dim.output(2))/2];
dim.max_offset = dim.data(1:2)+dim.min_offset-dim.output;
dim.ratio = dim.input./dim.output;

% test file
test_file = strrep('@train_file@','-train.prototxt',sprintf('-test.prototxt'));
fid       = fopen(test_file,'w');
fprintf(fid, 'input: "data"\n');
fprintf(fid, 'input_shape: { dim: %g dim: %g dim: %g dim: %g}\n', ...
       1, dim.data(3), dim.data(2), dim.data(1));
fprintf(fid, 'input: "def"\n');
fprintf(fid, 'input_shape: { dim: %g dim: %g dim: %g dim: %g}\n', ...
        1, dim.input(2), dim.input(1), 2);
fprintf(fid, 'state: { phase: TEST }\n'); 
fwrite(fid, train_prototxt);
fclose(fid);

for p=1:1,% subject
  % net: network 
  d = dir(fullfile('@snapshotdir@',sprintf('2d_dense_snapshot_iter_*.caffemodel.h5')));
  numel(d)
  for dd = 1:numel(d),
    %[~, nIdx] = max([d.datenum]);
    lastunderscore = strfind(d(dd).name,'_');
    lastunderscore = lastunderscore(end);
    iter = str2num(d(dd).name(lastunderscore+1:end-11));
    predfile = dir(sprintf(fullfile('@snapshotdir@','pred_%d_iter_%d.h5'),p,iter));
    if ~isempty(predfile) && (predfile.datenum>d(dd).datenum), continue; end
    fprintf(sprintf('Computing segmentation for subject %02d iteration %d ..',p,iter));
    snapshotd='@snapshotdir@';
    cmd = ['net = caffe.Net(''' test_file ''',' ...
                'fullfile(snapshotd,d(dd).name),''test'');'];
   % 'caffe command:', cmd
    evalc(cmd);


    % pred: prediction
    pred.TRAIN = NaN([fliplr(dim.tiles).*dim.output 2 1],'single');
   % 'having problems at this point', dim.tiles, dim.output, dim.tiles.*dim.output

    for i=0:dim.tiles(1)-1,       % width
      for j=0:dim.tiles(2)-1,     % height
          [X Y] = ndgrid((0:dim.input(1)-1)+dim.min_offset(1)+i*dim.output(1),  ...
                            (0:dim.input(2)-1)+dim.min_offset(2)+j*dim.output(2));
         % 'grid created'
          def = single(permute( cat(3,Y,X), [3 1 2]));
          %'size def:', size(def)
          % forward pass
          out = net.forward( {data(:,:,:,:,p); def});
        %  'out initiated'
          % size(out{1})
          % fill matrix of predictions

          pred.TRAIN((1:dim.output(1))+i*dim.output(1), (1:dim.output(2))+j*dim.output(2),:,1)  = out{1};
        
      end
    end
   % 'did it reach this point'
    % crop to original image size
    pred.TRAIN = pred.TRAIN(1:dim.data(1),1:dim.data(2),:,:);
    'pred.train size:', size(pred.TRAIN)

    % compute hard predictions
    
    %[~, pred.TRAIN] = max(permute(pred.TRAIN,[1 2 4 3]),[],3);
    msg = 'Error occurred. at this spoet';
    %error(msg)
    [~, pred.TRAIN] = max(permute(pred.TRAIN,[1 2 3]),[],3); 
    msg = 'Error occurred.';
    %error(msg)
    size(pred.TRAIN)
    pred.TRAIN = cast(pred.TRAIN,'uint8');
    
    % save predictions to disc
    h5outputfile = sprintf(fullfile('@snapshotdir@','pred_%d_iter_%d.h5'),p,iter);
    h5create(h5outputfile,'/decision',size(pred.TRAIN),'Datatype',class(pred.TRAIN));
    h5write(h5outputfile,'/decision',pred.TRAIN);
    h5writeatt(h5outputfile,'/decision','element_size_um', 1 .* [1.0 1.0 1.0]);
    fprintf('done\n');
    
    %% cleanup
    caffe.reset_all();

  end
end
EOF

    LD_PRELOAD=`gcc -print-file-name=libstdc++.so.6` /misc/software/matlab/R2015a/bin/matlab -nodisplay -r "dense_pred; exit"
    
else 
    echo snapshot not found
fi
