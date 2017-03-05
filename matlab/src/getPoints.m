function [row,col] = getPoints(path2Img)
    curImg = imread(path2Img);
   curImg = curImg(130:480,:,:);
   curImg = imresize(curImg,0.1);
   gray = rgb2gray(curImg);
   filtered = medfilt2(gray,[5 5]);
   ed = edge(filtered,'canny');
   [row,col]=find(ed==1);
end