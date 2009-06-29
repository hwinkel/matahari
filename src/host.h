#include <qpid/management/Manageable.h>
#include <qpid/management/ManagementObject.h>
#include <qpid/agent/ManagementAgent.h>

#include "qmf/com/redhat/nodereporter/Host.h"

#include "cpu.h"
#include "nic.h"

using namespace qpid::management;
using namespace std;

using qpid::management::Manageable;

class HostWrapper : public Manageable
{
    static HostWrapper *hostSingleton;

    friend ostream& operator<<(ostream &output, const HostWrapper& host);
    
    // Host Parameters
    string uuid;
    string hostname;
    string hypervisor;
    string arch;
    bool beeping;
    int memory;

    // Aggregated components
    vector<CPUWrapper*> cpus;
    vector<NICWrapper*> nics;

    // QMF related fields
    ManagementAgent *agent;
    qmf::com::redhat::nodereporter::Host *mgmt_object;

    // Methods to put up / take down QMF objects
    void setupQMFObjects(ManagementAgent *agent);
    void cleanupQMFObjects(void);

    // Housekeeping methods
    void syncQMFHostObject(void);
    void cleanupMemberObjects(void);

    // Host functionality
    void reboot();
    void shutdown();

    // Constructors and Destructor are private
    HostWrapper() {}
    HostWrapper(const HostWrapper &) {}
    ~HostWrapper() {}

 public:
    // Factory methods to create/dispose of the singleton
    static HostWrapper *setupHostWrapper(ManagementAgent *agent);
    static void disposeHostWrapper(void);

    // QMF Methods
    ManagementObject* GetManagementObject(void) const { return mgmt_object; }
    status_t ManagementMethod(uint32_t methodId, Args& args, string& text);
   
    // Field Accessors
    const string &getUUID(void) { return uuid; }
    const string &getHostname(void) { return hostname; }
    const string &getHypervisor(void) { return hypervisor; }
    const string &getArch(void) { return arch; }
    bool isBeeping(void) { return beeping; }
    int getMemory(void) { return memory; }

    const vector<CPUWrapper*> &getCPUList(void) { return cpus; }
    const vector<NICWrapper*> &getNICList(void) { return nics; }
};

