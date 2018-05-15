train_file = textread('filenames','%s', 'delimiter','\n','whitespace','');
test_files = textread('filenames','%s', 'delimiter','\n','whitespace','');

a = zeros(length(test_files),1);

for i=1:length(test_files),

        true_name = sprintf('training/%s', train_files{i});
        test_name = sprintf('training/%s', test_files{i});
        
        ref = imread(true_name);
        ref = im2single(ref); 
        input = imread(test_name);
        input = im2single(input);
        
        numPixels = numel(input);
        sqrdErr = sum((input(:) - ref(:)).^2) / numPixels;
        errEst = 10 * log10(1/sqrdErr);

        a(i) = errEst


end
average = mean(a);
disp(average);





