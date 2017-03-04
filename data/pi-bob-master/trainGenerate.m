Files=dir('./data/training/*.jpg');
labels = zeros(1,length(Files));
trainingSet = zeros(length(Files),300,2);
trainingNames = cell([1,length(Files)]);
for k=1:length(Files)
   FileName=Files(k).name;
   if(FileName(1)=='l')
       labels(k) = 1;
   elseif(FileName(1)=='r')
       labels(k) = 3;
   else 
       labels(k) = 2;    
   end
   
   [row,col] = getPoints(strcat('./data/training/',FileName));
   row(length(row)+1:300) = 0;
   col(length(col)+1:300) =0;
   trainingSet(k,:,1) = row';
   trainingSet(k,:,2) = col';
   trainingNames(k) = cellstr(strcat('./data/training/',FileName));
end
save trainPoints.mat trainingSet trainingNames