#include <cstdio>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <stdexcept>

#include "nvkms-ioctl.h"
#include "nvkms-api.h"
#include "nvUnixVersion.h"

// ------------------------------------------------------------------------------------------------|

std::vector<int> vibrance;

void read_vibrance_levels(char* argv[], int argc) {
    if (argc < 2) {
        printf("nVibrant: Usage: %s <vibrances per display, -1024 to 1023>\n", argv[0]);
        exit(1);
    }

    for (int i=0; i<(argc - 1); i++) {
        vibrance.push_back(atoi(argv[i+1]));

        if (vibrance[i] < -1024 || vibrance[i] > 1023) {
            printf("nVibrant: Vibrance level %d must be between -1024 and 1023\n", vibrance[i]);
            exit(1);
        }
    }
}

// Default to zero if not given on command line
int get_vibrance_level(unsigned int index) {
    if (index < vibrance.size())
        return vibrance.at(index);
    return 0;
}

// ------------------------------------------------------------------------------------------------|

int main(int argc, char *argv[]) {
    NvKmsIoctlParams* params = new struct NvKmsIoctlParams();
    read_vibrance_levels(argv, argc);
    int ioctl_retcode;

    // Open the nvidia-modeset file descriptor
    int modeset = open("/dev/nvidia-modeset", O_RDWR);

    if (modeset < 0) {
        perror("nVibrant: Failed to open /dev/nvidia-modeset");
        return modeset;
    }

    // ------------------------------------------|

    // Initialize nvkms to get a deviceHandle, dispHandle, etc.
    struct NvKmsAllocDeviceParams* allocDevice = new struct NvKmsAllocDeviceParams();
    strcpy(allocDevice->request.versionString, NV_VERSION_STRING);
    allocDevice->request.deviceId = 0; // Fixme: Will it always be zero?
    allocDevice->request.sliMosaic = NV_FALSE;
    allocDevice->request.tryInferSliMosaicFromExistingDevice = NV_FALSE;
    allocDevice->request.no3d = NV_TRUE;
    allocDevice->request.enableConsoleHotplugHandling = NV_FALSE;
    params->cmd     = NVKMS_IOCTL_ALLOC_DEVICE;
    params->size    = sizeof(struct NvKmsAllocDeviceParams);
    params->address = (NvU64) allocDevice;
    ioctl_retcode   = ioctl(modeset, NVKMS_IOCTL_IOWR, params);

    // Catch and warn common errors
    if (ioctl_retcode < 0) {
        switch (allocDevice->reply.status) {
            case NVKMS_ALLOC_DEVICE_STATUS_VERSION_MISMATCH:
                printf("nVibrant: Driver version mismatch, expected %s\n", NV_VERSION_STRING);
                break;
            default:
                printf("nVibrant: ioctl failed with error %d\n", allocDevice->reply.status);
                break;
        }
        return allocDevice->reply.status;
    }

    // ------------------------------------------|

    // Iterate on all GPUs (displays) in the system, querying their info
    for (NvU32 gpu=0; gpu<allocDevice->reply.numDisps; gpu++) {
        printf("nVibrant: GPU %d: Finding all connectors\n", gpu);
        NvKmsQueryDispParams* queryDisp = new struct NvKmsQueryDispParams();
        queryDisp->request.deviceHandle = allocDevice->reply.deviceHandle;
        queryDisp->request.dispHandle   = allocDevice->reply.dispHandles[gpu];
        params->cmd     = NVKMS_IOCTL_QUERY_DISP;
        params->size    = sizeof(struct NvKmsQueryDispParams);
        params->address = (NvU64) queryDisp;
        ioctl_retcode   = ioctl(modeset, NVKMS_IOCTL_IOWR, params);
        if (ioctl_retcode < 0) {
            printf("nVibrant: QueryDisp ioctl failed with error %d\n", ioctl_retcode);
            return ioctl_retcode;
        }

        // Iterate on all physical connections of the GPU (literally, hdmi, dp, etc.)
        for (NvU32 connector=0; connector<queryDisp->reply.numConnectors; connector++) {
            NvKmsQueryConnectorStaticDataParams* queryConnector = new struct NvKmsQueryConnectorStaticDataParams();
            queryConnector->request.deviceHandle    = allocDevice->reply.deviceHandle;
            queryConnector->request.dispHandle      = allocDevice->reply.dispHandles[gpu];
            queryConnector->request.connectorHandle = queryDisp->reply.connectorHandles[connector];
            params->cmd     = NVKMS_IOCTL_QUERY_CONNECTOR_STATIC_DATA;
            params->size    = sizeof(struct NvKmsQueryConnectorStaticDataParams);
            params->address = (NvU64) queryConnector;
            ioctl_retcode   = ioctl(modeset, NVKMS_IOCTL_IOWR, params);
            if (ioctl_retcode < 0) {
                printf("nVibrant: QueryConnector ioctl failed with error %d\n", ioctl_retcode);
                continue;
            }

            // Make the request to set digital vibrance for this monitor
            NvKmsSetDpyAttributeParams* setDpyAttr = new struct NvKmsSetDpyAttributeParams();
            setDpyAttr->request.deviceHandle = allocDevice->reply.deviceHandle;
            setDpyAttr->request.dispHandle   = allocDevice->reply.dispHandles[gpu];
            setDpyAttr->request.dpyId        = queryConnector->reply.dpyId;
            setDpyAttr->request.attribute    = NV_KMS_DPY_ATTRIBUTE_DIGITAL_VIBRANCE;
            setDpyAttr->request.value        = get_vibrance_level(connector);
            params->cmd     = NVKMS_IOCTL_SET_DPY_ATTRIBUTE;
            params->size    = sizeof(struct NvKmsSetDpyAttributeParams);
            params->address = (NvU64) setDpyAttr;
            ioctl_retcode   = ioctl(modeset, NVKMS_IOCTL_IOWR, params);
            if (ioctl_retcode < 0)
                continue;
            printf("nVibrant: • Display %d: Set vibrance to %d\n",
                connector, get_vibrance_level(connector));
        }
    }

    return 0;
}