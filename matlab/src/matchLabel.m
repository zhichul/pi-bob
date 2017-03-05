function [computedLabels,C] = matchLabel(trainingSet,trainingLabel, path2TestImg)
C = zeros(3,3);
Files=dir(path2TestImg);
labels = uint8(zeros(1,length(Files)));
computedLabels = uint32(zeros(1,length(Files)));
    for k=1:length(Files)
        FileName=Files(k).name;
        if(FileName(1)=='l')
            labels(k) = 1;
        elseif(FileName(1)=='r')
            labels(k) = 3;
        else 
            labels(k) = 2;    
        end
        [row,col] = getPoints(strcat('./data/testing/',FileName));
        
        distMat = zeros(1,length(trainingSet(:,1,1)));
        for j =1:length(trainingSet(:,1,1))
            avgDist = zeros(1,length(row));
            i =1;
            while  i<=length(row) && row(i)~=0 && col(i)~=0
               tempDist = (row(i)-trainingSet(j,:,1)).^2 + (col(i)-trainingSet(j,:,2)).^2;
               avgDist(i)= min(tempDist);
               i=i+1;
            end
            avgDist = find(avgDist~=0);
            distMat(j) = sum(avgDist(10:59));
        end
        [~,ind] = min(distMat);
        computedLabels(k) = trainingLabel(ind);
        C(labels(k), computedLabels(k)) = C(labels(k),computedLabels(k))+1;
    end
end