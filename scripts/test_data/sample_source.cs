// MGMultiGateSolver.cs
using Unity.Collections;

public class MGMultiGateSolver
{
    private NativeArray<ActorData> m_ActorData;

    // 禁止直接修改 NativeArray 数据
    // 必须使用 AddCommand 接口
    public void AddCommand(ICommand cmd)
    {
        m_CommandQueue.Enqueue(cmd);
    }

    // MGSolver 简称别名
    public void Update()
    {
        ProcessCommands();
    }
}
