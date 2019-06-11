% Load image
img = imread('initial_image.jpg'); 

% Full rotation matrix. Z-axis included, but not used.
R_rot = R_y(-60)*R_x(10)*R_z(0); 

% Strip the values related to the Z-axis from R_rot
R_2d  = [   R_rot(1,1)  R_rot(1,2) 0; 
            R_rot(2,1)  R_rot(2,2) 0;
            0           0          1    ]; 

% Generate transformation matrix, and warp (matlab syntax)
tform = affine2d(R_2d);
outputImage = imwarp(img,tform);

% Display image
figure(1), imshow(outputImage);



%*** Rotation Matrix Functions ***%

%% Matrix for Yaw-rotation about the Z-axis
function [R] = R_z(psi)
    R = [cosd(psi) -sind(psi) 0;
         sind(psi)  cosd(psi) 0;
         0          0         1];
end

%% Matrix for Pitch-rotation about the Y-axis
function [R] = R_y(theta)
    R = [cosd(theta)    0   sind(theta);
         0              1   0          ;
         -sind(theta)   0   cosd(theta)     ];
end

%% Matrix for Roll-rotation about the X-axis
function [R] = R_x(phi)
    R = [1  0           0;
         0  cosd(phi)   -sind(phi);
         0  sind(phi)   cosd(phi)];
end