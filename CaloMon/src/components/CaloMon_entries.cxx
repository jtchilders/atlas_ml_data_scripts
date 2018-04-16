#include "CaloMon/MyAlg.h"
#include "CaloMon/MyAlgHits.h"
#include "GaudiKernel/DeclareFactoryEntries.h"
DECLARE_ALGORITHM_FACTORY( MyAlg  )
DECLARE_ALGORITHM_FACTORY( MyAlgHits  )
DECLARE_FACTORY_ENTRIES( CaloMon ) {
DECLARE_ALGORITHM( MyAlg )
DECLARE_ALGORITHM( MyAlgHits )
}
