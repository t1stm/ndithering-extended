#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <stdlib.h>
#include <string.h>

#include "nvkms-ioctl.h"
#include "nvkms-api.h"

// Todo: Make configurable via CLI, target different drivers, etc.
#define DRIVER_VERSION "570.133.07"
#define VIBRANCE_LEVEL 1023

struct NvKmsIoctlParams* params;
struct NvKmsAllocDeviceParams* allocDevice;
struct NvKmsQueryDispParams* queryDisp;
struct NvKmsQueryConnectorStaticDataParams* queryConnector;
struct NvKmsSetDpyAttributeParams* setDpyAttr;
long returncode = 0;

int main(void) {
    params = (struct NvKmsIoctlParams*) calloc(1, sizeof(struct NvKmsIoctlParams));

    // Open the nvidia-modeset file device
    int modeset = open("/dev/nvidia-modeset", O_RDWR);
    if (modeset < 0) {
        perror("nVibrant: Failed to open modeset device");
        returncode = modeset;
        goto cleanup;
    }

    // --------------------------------------------------------------------------------------------|

    // Call NVKMS_IOCTL_ALLOC_DEVICE to initialize and get a NVKMS control object
    struct NvKmsAllocDeviceParams* allocDevice = calloc(1, sizeof(struct NvKmsAllocDeviceParams));
    snprintf(allocDevice->request.versionString, NVKMS_NVIDIA_DRIVER_VERSION_STRING_LENGTH, DRIVER_VERSION);
    allocDevice->request.deviceId = 0;
    allocDevice->request.sliMosaic = NV_FALSE;
    allocDevice->request.tryInferSliMosaicFromExistingDevice = NV_FALSE;
    allocDevice->request.no3d = NV_TRUE;
    allocDevice->request.enableConsoleHotplugHandling = NV_FALSE;
    params->cmd     = NVKMS_IOCTL_ALLOC_DEVICE;
    params->size    = sizeof(struct NvKmsAllocDeviceParams);
    params->address = (NvU64)allocDevice;
    returncode      = ioctl(modeset, NVKMS_IOCTL_IOWR, params);

    // Catch and warn common errors
    if (returncode < 0) {
        switch (allocDevice->reply.status) {
            case NVKMS_ALLOC_DEVICE_STATUS_VERSION_MISMATCH:
                printf("nVibrant: ioctl failed with driver version mismatch\n");
                break;
            default:
                printf("nVibrant: ioctl failed with error %d\n", allocDevice->reply.status);
                break;
        }
        goto cleanup;
    }

    // --------------------------------------------------------------------------------------------|

    // Iterate on all GPUs (displays) in the system, querying their info
    for (NvU32 gpu=0; gpu<allocDevice->reply.numDisps; gpu++) {
        printf("nVibrant: Applying setting for GPU %d\n", gpu);
        queryDisp = calloc(1, sizeof(struct NvKmsQueryDispParams));
        queryDisp->request.deviceHandle = allocDevice->reply.deviceHandle;
        queryDisp->request.dispHandle   = allocDevice->reply.dispHandles[gpu];
        params->cmd     = NVKMS_IOCTL_QUERY_DISP;
        params->size    = sizeof(struct NvKmsQueryDispParams);
        params->address = (NvU64)queryDisp;
        returncode      = ioctl(modeset, NVKMS_IOCTL_IOWR, params);
        if (returncode < 0) {
            printf("nVibrant: QueryDisp ioctl failed with error %ld\n", returncode);
            goto cleanup;
        }

        // Iterate on all physical connections of the GPU (literally, hdmi, dp, etc.)
        for (int connector=0; connector<queryDisp->reply.numConnectors; connector++) {
            queryConnector = calloc(1, sizeof(struct NvKmsQueryConnectorStaticDataParams));
            queryConnector->request.deviceHandle    = allocDevice->reply.deviceHandle;
            queryConnector->request.dispHandle      = allocDevice->reply.dispHandles[gpu];
            queryConnector->request.connectorHandle = queryDisp->reply.connectorHandles[connector];
            params->cmd     = NVKMS_IOCTL_QUERY_CONNECTOR_STATIC_DATA;
            params->size    = sizeof(struct NvKmsQueryConnectorStaticDataParams);
            params->address = (NvU64)queryConnector;
            returncode      = ioctl(modeset, NVKMS_IOCTL_IOWR, params);
            if (returncode < 0) {
                printf("nVibrant: QueryConnector ioctl failed with error %ld\n", returncode);
                continue;
            }

            // Make the request to set digital vibrance for this monitor
            setDpyAttr = calloc(1, sizeof(struct NvKmsSetDpyAttributeParams));
            setDpyAttr->request.deviceHandle = allocDevice->reply.deviceHandle;
            setDpyAttr->request.dispHandle = allocDevice->reply.dispHandles[gpu];
            setDpyAttr->request.dpyId = queryConnector->reply.dpyId;
            setDpyAttr->request.attribute = NV_KMS_DPY_ATTRIBUTE_DIGITAL_VIBRANCE;
            setDpyAttr->request.value = VIBRANCE_LEVEL;
            params->cmd     = NVKMS_IOCTL_SET_DPY_ATTRIBUTE;
            params->size    = sizeof(struct NvKmsSetDpyAttributeParams);
            params->address = (NvU64) setDpyAttr;
            returncode      = ioctl(modeset, NVKMS_IOCTL_IOWR, params);
            if (returncode < 0)
                continue;
            printf("nVibrant: • Set vibrance on connection %d\n", connector);
        }
    }

    returncode = 0;

cleanup:
    close(modeset);
    return returncode;
}
