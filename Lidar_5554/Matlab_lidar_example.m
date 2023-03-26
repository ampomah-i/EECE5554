
ptCloud = pcread("Pandaset_subset/2459.pcd");

lower = min([ptCloud.XLimits ptCloud.YLimits]);
upper = max([ptCloud.XLimits ptCloud.YLimits]);
  
xlimits = [lower upper];
ylimits = [lower upper];
zlimits = ptCloud.ZLimits;

player = pcplayer(xlimits,ylimits,zlimits);

xlabel(player.Axes,'X (m)');
ylabel(player.Axes,'Y (m)');
zlabel(player.Axes,'Z (m)');

view(player,ptCloud); 
