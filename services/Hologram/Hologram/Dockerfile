FROM mono:5.4.1.6
WORKDIR /home/Hologram/
CMD nuget restore && \
	msbuild /p:Configuration=Release \
			/p:DeployType=ReadyToUpload \
			/t:rebuild Hologram.sln && \
	mkdir -p bin/Release/dump && \
	mono bin/Release/Hologram.exe
